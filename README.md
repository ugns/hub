# Anchore Hub

The Anchore Hub is a centralized repository of resources that are served and then can be loaded into/consumed by [Anchore Engine](https://github.com/anchore/anchore-engine), via anchore engine clients.  This repository serves as the canonical store of source documents (initially, [Anchore Policy Bundles](https://anchore.freshdesk.com/support/solutions/articles/36000074705-policy-bundles-and-evaluation)), both serving as a location where pre-defined policy bundles can be easily fetched and loaded into Anchore Engine deployments to help with a starting point for creating your own bundles, as well as a location where users of Anchore can submit and share new policy bundles and, moving forward, other Anchore resources as well.

## Structure

The structure of this repository is meant to facilitate a straight-forward mechanism for users to contribute new documents, or modify existing documents, with a light-weight process for translating the source documents into an indexed, static structure that can easily be hosted by any HTTP server.  By default, all documents stored here are automatically converted into such a static site, hosted publicly, and is made immediately available to any client that can communicate with the public Anchore Hub (initially, the Anchore CLI).  

The important items in this repo are as follows:

- [source/bundles](https://github.com/anchore/hub-dev/tree/master/sources/bundles): location of fully functional anchore policy bundles, ready to load as usuable anchore policy bundles.  For more information on the anchore policy bundle format/capabilities, see the [anchore policy bundles and evaluation guide](https://anchore.freshdesk.com/support/solutions/articles/36000074705-policy-bundles-and-evaluation)
- [generate.py](https://github.com/anchore/hub-dev/blob/master/generate.py): script that converts the source documents (bundles in source/bundles) into static content, performing document format validation as well as light conversion of some items in the source documents.

## Submitting a New Policy 

To submit a new policy bundle for consideration, the process at a high level should be:

1. Read and accept the terms of the [contributor agreement](https://github.com/anchore/hub-dev/blob/master/CONTRIBUTING.rst)
2. create/modify a anchore policy bundle, and remove any site-specific information from the bundle document ideally
3. clone a version of this repository locally, and put your new bundle in the sources/bundles/ directory, using a unique name for the bundle that reflects it's purpose (i.e. anchore_dockerfile_bestpractive_checks.json)
4. run the './generate.py' script locally to perform validation of the new bundle, and inspect the output bundle to ensure it is correct (by default, ./generate.py will create a static site in /tmp/targethtml for inspection/test)
5. Create a PR with the new bundle included, including an explaination of the new bundle and it's purpose.  Be sure to sign off on the PR according the the [contributor agreement](https://github.com/anchore/hub-dev/blob/master/CONTRIBUTING.rst).

## Modifying an Existing Policy

To modify an existing policy bundle, the steps are the same as above, replacing the new bundle steps with your modifications to an existing bundle, along with comments/explaination in the PR about the nature of the change.

## Using the Hub

All bundles in this repository are automatically served via a publicly accessible HTTP service.  Presently, the Anchore CLI is a client that includes an operation for interacting with the hub, allowing available bundles to be listed, fetched (for review) or directly installed into a local anchore engine deployment.  A quick example of interacting with the hub follows:

```
# anchore-cli policy hub list
ame                           Description                           Updated                           
anchore_security_only          Includes a single policy that         2019-01-25T01:08:47.518134        
                               only performs a variety of                                              
                               security checks.                                                        
anchore_default_bundle         Default Anchore Engine policy         2019-01-25T01:08:47.518134        
                               checks, single mapping for all                                          
                               images, empty whitelist.                                                
anchore_cis_1.13.0_base        Docker CIS 1.13.0 image               2019-01-25T01:08:47.518134        
                               content checks, from section 4                                          
                               and 5. NOTE: some parameters                                            
                               (generally are named                                                    
                               'example...') must be modified                                          
                               as they require site-specific                                           
                               settings                                                                
#
# anchore-cli policy hub get anchore_cis_1.13.0_base > /tmp/anchore_cis_1.13.0_base.json
# <use favorite editor to look at the raw bundle document itself>
#
# anchore-cli policy hub install anchore_cis_1.13.0_base
Policy ID: anchore_cis_1.13.0_base
Active: False
Source: local
Created: 2019-01-28T18:31:52Z
Updated: 2019-01-28T18:31:52Z
#
# anchore-cli policy list
Policy ID                                   Active        Created                     Updated                     
fff177bd-5661-4d4a-a740-f797ef25d75f        True          2018-11-30T01:09:44Z        2019-01-24T21:12:16Z        
...
...
anchore_cis_1.13.0_base                     False         2019-01-28T18:31:52Z        2019-01-28T18:31:52Z        
...
...
#
```

From here, you can now interact with the installed anchore policy bundle using anchore-cli, Anchore Enterprise UI, or the anchore engine API directly.

## Deploying an On-Prem Hub

By default, when new resources are stored in this repository, or modifications are made, an automated process is executed to execute ./generate.py and serve the content via a publicly available site hosted at (TBD).  Alternatively, you may opt to run your own, internal, anchore hub using the tools in this repo, serving the data output by ./generate.py from any HTTP service you operate.  The clients (such as anchore-cli) can then be directed at this new location instead of the default public hub URL, and the rest of the operations will perform as described above. 

For example, if a local hub has been populated at a local URL "http://myhost.com/anchorehub", the anchore-cli can be configured to use that location (initially looking for "http://myhost.com/anchorehub/index.json") instead of the default:

```
# export ANCHORE_CLI_HUB_URL=http://myhost.com/anchorehub"
# anchore-cli policy hub list
<list of your locally generated hub documents>
```
