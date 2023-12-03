# ansible-module-demo

The aim of this repo is to help you get started developing
simple custom modules for Ansible.

## Dev environment prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- Python3 interpreter
- [docker-compose](https://docs.docker.com/compose/install/)

## Testing your module

Once you have the dev environment ready, you can test
your module by running playbooks.

To do that, you must tell Ansible this is part of its "Library".
That makes it aware it can find modules in this directory.

```
# make the ansible version installed via `make dev`
# available to you
source venv/bin/activate
export ANSIBLE_LIBRARY=$(pwd)/plugins/modules
# this triggers the snipeit_category module, found in
# plugins/modules
ansible-playbook dev_playbooks/create_category.yml
ansible-playbook dev_playbooks/create_model.yml # needs the category
ansible-playbook dev_playbooks/create_entry.yml # needs the model
ansible-playbook dev_playbooks/delete_entry.yml # needs the model

```

## Dev environment setup

To create the venv, bring up the database and snipe-it, run:

```

make dev

```

The web app will be port-forwarded to `localhost:8080`

This does not go through the initial setup of snipe-it.
For convenience, a DB dump with a basic setup is included - you can run:

```

# wait 5 seconds if you just ran `make dev`
# otherwise you might run into a lock 
# no big issue if you accidentally do, just run it again
make setup-db

```

Anytime you run this, it will reset the dev environment to a barebones setup
with `admin`/`password` set as the login credentials.

It's helpful if you make a lot of changes and you'd like to reset to a clean state.

To bring down the containers and delete volumes,
but keep the virtual environment, run:

```

make down

```

To clean up everything, including the venv:

```

make clean

```

To install python requirements and requirements-dev:

```

make deps

```

To only clean the venv:

```

make clean-venv

```

And to re-create the venv:

```

make venv

```

## Extra information

Development docs from ansible can be found here: https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

### Shipping modules

The most common way to ship modules is to include them in a collection.
This repository follows a similar structure - to generate it I used:

```

ansible-galaxy collection init danielpodwysocki.ansible_module_demo

```

You can read more about how you can leverage those here:
https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_creating.html#creating-a-collection-skeleton

For collections for internal use, I recommend installing them directly from git

- ansible-galaxy supports that and you can keep them in your internal repos that way.

A good pattern is to pin the version to a commit hash and let a dependency tool like `renovate` keep it up to date.
This enables you to later integrate any tests easily.
