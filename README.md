# Ansible Collection - nttmcp.mcp

Ansible Modules to support the NTT Managed Cloud Platform (MCP)


## Requirements

### Python Modules

* requests
* configparser
* pyOpenSSL
* netaddr

To install these modules execute:

> pip install --user requests configparser PyOpenSSL netaddr


## Installation

ansible-galaxy collection install nttmcp.mcp


## Authentication

One of the following three methods can be used to provide API credentials and connection information

* Module arguments
* Credential File
* Environment Variables

### Module Arguments

Each module supports an optional argument of type dictionary that contains the following attributes:

* username (Cloud Control username)
* password (Cloud Control password)
* api (Cloud Control API endpoint)
* api_version (Cloud Control API version)

Examples (hint: use ansible-vault to encrypt the password strings):

```YAML
- name: List Cloud Network Domains:
  nttmcp.mcp.network_info:
    auth:
      username: myuser
      password: mypassword
      api: api-na.mcp-services.net
      api_version: 2.11
    region: na
    datacenter: NA9
```

OR using variables

```YAML
- hosts: localhost
  connection: local
  gather_facts: no
  vars:
    auth:
      username: myuser
      password: mypassword
      api: api-na.mcp-services.net
      api_version: 2.11
  tasks:
  - name: List Cloud Network Domains:
    nttmcp.mcp.network_info:
      auth: "{{auth}}"
      region: na
      datacenter: NA9
```

### Credential File

Configure Cloud Control credentials by creating/editing a `.nttmcp` file in your home directory containing the following information:

    [nttmcp]
    NTTMCP_API: api-<geo>.mcp-services.net
    NTTMCP_API_VERSION: 2.10
    NTTMCP_PASSWORD: mypassword
    NTTMCP_USER: myusername

### Environment Variables

Use environment variables:

```Shell
set +o history
export NTTMCP_API=api-<geo>.mcp-services.net
export NTTMCP_API_VERSION=2.10
export NTTMCP_PASSWORD=mypassword
export NTTMCP_USER=myusername
set -o history
```
