#!/usr/bin/env python3

import json
import os
import re
import hashlib
import time
import datetime
import sys
import yaml
import jsonref
import jsonschema
from shutil import copyfile

def process_bundles(source_dir=None, target_dir=None):
    bundles = {}
    source_dir = source_dir
    bundle_dir = os.path.join(source_dir, "bundles")

    with open("./schemas/anchore-engine-api.yaml", 'r') as FH:
        anchore_engine_api_swagger = jsonref.loads(json.dumps(yaml.safe_load(FH)))
        bundleschema = anchore_engine_api_swagger['definitions']['PolicyBundle']

    if os.path.isdir(bundle_dir):
        for bundlefile in os.listdir(bundle_dir):
            patt = re.match("(.*)\.json$", bundlefile)
            if patt:
                bundlename = patt.group(1)
                thefile = os.path.join(bundle_dir, bundlefile)
                try:
                    print ("\tOpening bundle {}...".format(thefile), end='')
                    with open(thefile, 'r') as FH:
                        print ("done!")
                        buf = FH.read()
                        digest = "{}:{}".format("sha256", hashlib.sha256(buf.encode('utf8')).hexdigest())
                        bundle = json.loads(buf)
                        
                        print ("\tValidating bundle {}...".format(thefile), end='')
                        jsonschema.validate(bundle, bundleschema)
                        print ("done!")

                        print ("\tProcessing bundle {}...".format(thefile), end='')
                        bundle_record = {
                            'location': '/'.join(['bundles', bundlename, "{}.json".format(digest)]),
                            'type': 'bundle',
                            'name': bundlename,#bundle.get('name', 'N/A'),
                            'description': bundle.get('description', bundle.get('comment', "N/A")),
                            'digest': digest,
                        }
                        bundles[bundlename] = bundle_record
                        print ("done!")
                except Exception as err:
                    print("\nERROR parsing bundle {} - exception: {}".format(bundlefile, err))
                    raise err
    return(bundles)

def populate_target(source_dir=None, target_dir=None, bundles={}):

    # create the manifest
    manifest = {
        'metadata': {
            'digest': "",
            'last_updated': datetime.datetime.utcnow().isoformat(),
        },
        'content': []
    }
    manifest['content'] = list(bundles.values())
    digest = "{}:{}".format('sha256', hashlib.sha256(json.dumps(manifest['content'], sort_keys=True, indent=4).encode('utf8')).hexdigest())
    manifest['metadata']['digest'] = digest

    # prep the target location
    if not target_dir or not source_dir:
        raise Exception("empty target_dir({}) or source_dir({}) passed in".format(target_dir, source_dir))

    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    for subdir in ['bundles']:
        dst_dir = os.path.join(target_dir, subdir)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)

    # finally, copy/write all input and manifest data to the target location
    for bundlename in bundles.keys():
        src_file = os.path.join(source_dir, "bundles", "{}.json".format(bundlename))
        dst_dir = os.path.join(target_dir, "bundles", bundlename)
        if not os.path.isdir(dst_dir):
            os.mkdir(dst_dir)
        dst_file = os.path.join(dst_dir, "{}.json".format(bundles[bundlename]['digest']))
        with open(src_file, 'r') as FH:
            bundledata = json.loads(FH.read())
            bundledata['name'] = bundlename
            bundledata['id'] = bundlename
            with open(dst_file, 'w') as OFH:
                OFH.write(json.dumps(bundledata, indent=4, sort_keys=True))
        #copyfile(src_file, dst_file)

    manifestfile = os.path.join(target_dir, "index.json")
    with open(manifestfile, 'w') as OFH:
        OFH.write(json.dumps(manifest, sort_keys=True, indent=4))

    src_file = os.path.join(source_dir, "static", "index.html")
    dst_file = os.path.join(target_dir, "index.html")
    copyfile(src_file, dst_file)

    return(True)

# environment settings
defaults = [
    ("ANCHORE_HUB_TARGETDIR", "/tmp/targethtml"),
    ("ANCHORE_HUB_SOURCEDIR", "./sources"),
]
config = {}
for e,default in defaults:
    config[e] = os.environ.get(e, default)

print ("Using config:\n{}".format(json.dumps(config, indent=4, sort_keys=True)))

# process source bundles, returning bundle metadata
try:
    print ("Processing bundles...")
    bundles = process_bundles(source_dir=config.get("ANCHORE_HUB_SOURCEDIR"), target_dir=config.get("ANCHORE_HUB_TARGETDIR"))
    print ("Processing bundles done!")
except Exception as err:
    raise Exception("ERROR during bundle processing")

# generate target and populate
try:
    print ("Populating target...", end='')
    rc = populate_target(source_dir=config.get("ANCHORE_HUB_SOURCEDIR"), target_dir=config.get("ANCHORE_HUB_TARGETDIR"), bundles=bundles)
    print ("done!")
except Exception as err:
    raise Exception("ERROR during target population")


print ("All Done. Config used:\n{}".format(json.dumps(config, sort_keys=True, indent=4)))
exit(0)
