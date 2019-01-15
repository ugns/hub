#!/usr/bin/env python3

import json
import os
import re
import hashlib
import time
import datetime
import sys
from shutil import copyfile

def process_bundles(source_dir=None, target_dir=None, default_url=None):
    bundles = {}
    source_dir = source_dir
    bundle_dir = os.path.join(source_dir, "bundles")
    if os.path.isdir(bundle_dir):
        for bundlefile in os.listdir(bundle_dir):
            patt = re.match("(.*)\.json$", bundlefile)
            if patt:
                bundlename = patt.group(1)
                thefile = os.path.join(bundle_dir, bundlefile)
                try:
                    print ("Processing bundle {}".format(thefile))
                    with open(thefile, 'r') as FH:
                        buf = FH.read()
                        digest = "{}:{}".format("sha256", hashlib.sha256(buf.encode('utf8')).hexdigest())
                        bundle = json.loads(buf)

                        policies = []
                        for i in bundle['policies']:
                            idigest = "{}:{}".format("sha256", hashlib.sha256(json.dumps(i, sort_keys=True).encode('utf8')).hexdigest())
                            i_record = {
                                'name': i.get('name', "N/A"),
                                'description': i.get('description', i.get('comment', "N/A")),
                                'digest': idigest,
                            }
                            policies.append(i_record)

                        whitelists = []
                        for i in bundle['whitelists']:
                            idigest = "{}:{}".format("sha256", hashlib.sha256(json.dumps(i, sort_keys=True).encode('utf8')).hexdigest())
                            i_record = {
                                'name': i.get('name', "N/A"),
                                'description': i.get('description', i.get('comment', "N/A")),
                                'digest': idigest,
                            }
                            whitelists.append(i_record)

                        bundle_record = {
                            'location': '/'.join([default_url, 'bundles', bundlename, "{}.json".format(digest)]),
                            'type': 'bundle',
                            'name': bundlename,#bundle.get('name', 'N/A'),
                            'description': bundle.get('description', bundle.get('comment', "N/A")),
                            'digest': digest,
                            'policies': policies,
                            'whitelists': whitelists,
                        }
                        bundles[bundlename] = bundle_record
                except Exception as err:
                    print("ERROR parsing bundle {} - exception: {}".format(bundlefile, err))
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

    return(True)

# environment settings
defaults = [
    ("ANCHORE_HUB_TARGETDIR", "/tmp/targethtml"),
    ("ANCHORE_HUB_SOURCEDIR", "./sources"),
    ("ANCHORE_HUB_TARGETBASEURL", "http://localhost:8080/"),
]
config = {}
for e,default in defaults:
    config[e] = os.environ.get(e, default)

print ("Using config:\n{}".format(json.dumps(config, indent=4, sort_keys=True)))

# process source bundles, returning bundle metadata
print ("Processing bundles...")
bundles = process_bundles(source_dir=config.get("ANCHORE_HUB_SOURCEDIR"), target_dir=config.get("ANCHORE_HUB_TARGETDIR"), default_url=config.get("ANCHORE_HUB_TARGETBASEURL"))

# generate target and populate
print ("Populating target...")
rc = populate_target(source_dir=config.get("ANCHORE_HUB_SOURCEDIR"), target_dir=config.get("ANCHORE_HUB_TARGETDIR"), bundles=bundles)

print ("Done. Config used:\n{}".format(json.dumps(config, sort_keys=True, indent=4)))
exit(0)
