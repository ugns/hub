#!/usr/bin/env python3

import json
import os
import re
import hashlib
import time
import datetime
from shutil import copyfile

def process_bundles(target_dir=None, default_url=None):
    bundles = {}
    bundle_dir = "./bundles"
    if os.path.isdir(bundle_dir):
        for bundlefile in os.listdir(bundle_dir):
            if re.match(".*\.json$", bundlefile):
                thefile = os.path.join(bundle_dir, bundlefile)
                try:
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
                            'location': '/'.join([default_url, 'bundles', bundlefile]),
                            'type': 'bundle',
                            'name': bundle.get('name', 'N/A'),
                            'description': bundle.get('description', bundle.get('comment', "N/A")),
                            'digest': digest,
                            'policies': policies,
                            'whitelists': whitelists,
                        }
                        if thefile not in bundles:
                            bundles[thefile] = []
                        bundles[thefile].append(bundle_record)
                except Exception as err:
                    print("ERROR parsing bundle {} - exception: {}".format(bundlefile, err))
    return(bundles)

def populate_target(target_dir=None, bundles={}):

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
    if not target_dir:
        raise Exception("empty target_dir passed in")

    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    for subdir in ['bundles']:
        dst_dir = os.path.join(target_dir, subdir)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)

    # finally, copy/write all input and manifest data to the target location
    for bundlefile in bundles.keys():
        src_file = bundlefile
        dst_file = os.path.join(target_dir, bundlefile)
        copyfile(src_file, dst_file)

    manifestfile = os.path.join(target_dir, "manifest.json")
    with open(manifestfile, 'w') as OFH:
        OFH.write(json.dumps(manifest, sort_keys=True, indent=4))

    return(True)

# environment settings
defaults = [
    ("ANCHORE_HUB_TARGETDIR", "./targethtml"),
    ("ANCHORE_HUB_TARGETBASEURL", "http://localhost:8080/"),
]
config = {}
for e,default in defaults:
    config[e] = os.environ.get(e, default)

print ("Using config:\n{}".format(json.dumps(config, indent=4, sort_keys=True)))

# process source bundles, returning bundle metadata
print ("Processing bundles...")
bundles = process_bundles(target_dir=config.get("ANCHORE_HUB_TARGETDIR"), default_url=config.get("ANCHORE_HUB_TARGETBASEURL"))

# generate target and populate
print ("Populating target...")
rc = populate_target(target_dir=config.get("ANCHORE_HUB_TARGETDIR"), bundles=bundles)

print ("Done")
exit(0)
