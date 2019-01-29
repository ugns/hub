# Anchore Policy Hub

The Anchore Policy Hub is a centralized repository of resources that are served and then can be loaded into/consumed by [Anchore Engine](https://github.com/anchore/anchore-engine), via anchore engine clients.  This repository serves as the canonical store of source documents (initially, [Anchore Policy Bundles](https://anchore.freshdesk.com/support/solutions/articles/36000074705-policy-bundles-and-evaluation)), both serving as a location where pre-defined policy bundles can be easily fetched and loaded into Anchore Engine deployments to help with a starting point for creating your own bundles, as well as a location where users of Anchore can submit and share new policy bundles and, moving forward, other Anchore resources as well.

## Structure

The structure of this repository is meant to facilitate a straight-forward mechanism for users to contribute new policy documents, or modify existing policy documents, with a light-weight process for translating the source documents into an indexed, static structure that can easily be hosted by any HTTP server.  By default, all policy documents stored here are automatically converted into such a static site, hosted publicly, and is made immediately available to any client that can communicate with the public Anchore Policy Hub (initially, the Anchore CLI).  

The important items in this repo are as follows:

- [source/bundles](https://github.com/anchore/hub-dev/tree/master/sources/bundles): location of fully functional anchore policy bundles, ready to load as usuable anchore policy bundles.  For more information on the anchore policy bundle format/capabilities, see the [anchore policy bundles and evaluation guide](https://anchore.freshdesk.com/support/solutions/articles/36000074705-policy-bundles-and-evaluation)
- [generate.py](https://github.com/anchore/hub-dev/blob/master/generate.py): script that converts the source documents (bundles in source/bundles) into static content, performing document format validation as well as light conversion of some items in the source documents.

## Submitting a New Policy 

Before you being, please take care not to include any sensitive information in any documents that are submitted to this (publicly hosted) repository).  If you wish to centrally manage your own private hub, see the instructions at the end of this guide to understand how to host your own instance of an anchore hub.  To submit a new policy bundle for consideration, the process at a high level should be:

1. Read and accept the terms of the [contributor agreement](https://github.com/anchore/hub-dev/blob/master/CONTRIBUTING.rst)
2. create/modify a anchore policy bundle, and remove any site-specific information from the bundle document ideally
3. clone a version of this repository locally, and put your new bundle in the sources/bundles/ directory, using a unique name for the bundle that reflects it's purpose (i.e. anchore_dockerfile_bestpractive_checks.json)
4. run the './generate.py' script locally to perform validation of the new bundle, and inspect the output bundle to ensure it is correct (by default, ./generate.py will create a static site in /tmp/targethtml for inspection/test)
5. Create a PR with the new bundle included, including an explaination of the new bundle and it's purpose.  Be sure to sign off on the PR according the the [contributor agreement](https://github.com/anchore/hub-dev/blob/master/CONTRIBUTING.rst).

## Modifying an Existing Policy

To modify an existing policy bundle, the steps are the same as above, replacing the new bundle steps with your modifications to an existing bundle, along with comments/explaination in the PR about the nature of the change.

## Using the Hub

All bundles in this repository are automatically served via a publicly accessible HTTP service.  Presently, the [Anchore CLI](https://github.com/anchore/anchore-cli)(version >= 0.3.2) is a client that includes operations for interacting with the hub, allowing available bundles to be listed, fetched (for review) or directly installed into a local anchore engine deployment.  A quick example of interacting with the hub follows:

```
# anchore-cli policy hub list
Name                           Description                                                        
anchore_security_only          Includes a single policy that only performs a variety of           
                               security checks.                                                   
anchore_default_bundle         Default policy bundle that comes installed with vanilla            
                               anchore-engine deployments.  Mixture of light vulnerability        
                               checks, dockerfiles checks, and warning triggers for common        
                               best practices.                                                    
anchore_cis_1.13.0_base        Docker CIS 1.13.0 image content checks, from section 4 and         
                               5. NOTE: some parameters (generally are named 'example...')        
                               must be modified as they require site-specific settings            
                       
# anchore-cli policy hub get anchore_cis_1.13.0_base 
Policy Bundle ID: anchore_cis_1.13.0_base
Name: anchore_cis_1.13.0_base
Description: Docker CIS 1.13.0 image content checks, from section 4 and 5. NOTE: some parameters (generally are named 'example...') must be modified as they require site-specific settings

Policy Name: CIS File Checks
Policy Description: Docker CIS section 4.8 and 4.10 checks.

Policy Name: CIS Dockerfile Checks
Policy Description: Docker CIS section 4.1, 4.2, 4.6, 4.7, 4.9 and 5.8 checks.

Policy Name: CIS Software Checks
Policy Description: Docker CIS section 4.3 and 4.4 checks.

Whitelist Name: suid-wl-rhel
Whitelist Description: Example whitelist with triggerIds of files that are expected to have SUID/SGID, for rhel-based images

Whitelist Name: suid-wl-debian
Whitelist Description: Example whitelist with triggerIds of files that are expected to have SUID/SGID, for debian-based images

Mapping Name: default
Mapping Rule: */*:*
Mapping Policies: CIS Software Checks,CIS Dockerfile Checks,CIS File Checks
Mapping Whitelists: suid-wl-debian,suid-wl-rhel

# anchore-cli --json policy hub get anchore_cis_1.13.0_base > /tmp/anchore_cis_1.13.0_base.json
# <use favorite editor to look at the raw bundle document itself>

# anchore-cli policy hub install anchore_cis_1.13.0_base
Policy ID: anchore_cis_1.13.0_base
Active: False
Source: local
Created: 2019-01-28T18:31:52Z
Updated: 2019-01-28T18:31:52Z

# anchore-cli policy list
Policy ID                                   Active        Created                     Updated                     
fff177bd-5661-4d4a-a740-f797ef25d75f        True          2018-11-30T01:09:44Z        2019-01-24T21:12:16Z        
...
...
anchore_cis_1.13.0_base                     False         2019-01-28T18:31:52Z        2019-01-28T18:31:52Z        
...
...

```

From here, you can now interact with the installed anchore policy bundle using anchore-cli, Anchore Enterprise UI, or the anchore engine API directly.

## Deploying an On-Prem Hub

By default, when new resources are stored in this repository, or modifications are made, an automated process is executed to execute ./generate.py and serve the content via a publicly available site hosted at (TBD).  Alternatively, you may opt to run your own, internal, anchore hub using the tools in this repo, serving the data output by ./generate.py from any HTTP service you operate.  The clients (such as anchore-cli) can then be directed at this new location instead of the default public hub URL, and the rest of the operations will perform as described above. 

Below is an example process for running a local anchore hub using a docker nginx container, for testing and to illustrate the general process.  Permanent installations would use a similiar process but host the generated static content in a permanent HTTP server location instead of a local nginx container location:

```
# cd ./hub
# ./generate.py
Using config:
{
    "ANCHORE_HUB_SOURCEDIR": "./sources",
    "ANCHORE_HUB_TARGETDIR": "/tmp/targethtml"
}
Processing bundles...
	Opening bundle ./sources/bundles/anchore_default_bundle.json...done!
	Validating bundle ./sources/bundles/anchore_default_bundle.json...done!
	Processing bundle ./sources/bundles/anchore_default_bundle.json...done!
	Opening bundle ./sources/bundles/anchore_security_only.json...done!
	Validating bundle ./sources/bundles/anchore_security_only.json...done!
	Processing bundle ./sources/bundles/anchore_security_only.json...done!
	Opening bundle ./sources/bundles/anchore_cis_1.13.0_base.json...done!
	Validating bundle ./sources/bundles/anchore_cis_1.13.0_base.json...done!
	Processing bundle ./sources/bundles/anchore_cis_1.13.0_base.json...done!
Processing bundles done!
Populating target...done!
All Done. Config used:
{
    "ANCHORE_HUB_SOURCEDIR": "./sources",
    "ANCHORE_HUB_TARGETDIR": "/tmp/targethtml"
}

# find /tmp/targethtml/
/tmp/targethtml/
/tmp/targethtml/bundles
/tmp/targethtml/bundles/anchore_default_bundle
/tmp/targethtml/bundles/anchore_default_bundle/sha256:27c2c06db79dafdf4c2b51f489c2b1a55f86396470de3613cfb80201ec71da55.json
/tmp/targethtml/bundles/anchore_security_only
/tmp/targethtml/bundles/anchore_security_only/sha256:f9a08c92a04eb9575d98c41e0b72af23f194305592acdf95f9fe92f1c415550a.json
/tmp/targethtml/bundles/anchore_cis_1.13.0_base
/tmp/targethtml/bundles/anchore_cis_1.13.0_base/sha256:fcd085e288aefb5412cf55529fdbb8ae7c57ad3bc46946263db517e875788582.json
/tmp/targethtml/index.json

# docker run --name anchore-hub-nginx -v /tmp/targethtml/:/usr/share/nginx/html/:ro -p 8080:80 -d nginx

# export ANCHORE_CLI_HUB_URL=http://localhost:8080/"
# anchore-cli policy hub list
...
...
...
```
