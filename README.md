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

Configure Cloud Control credentials by creating/editing a `.nttmcp` file in your home directory containing the following information:

    [nttmcp]
    NTTMCP_API: api-<geo>.mcp-services.net
    NTTMCP_API_VERSION: 2.10
    NTTMCP_PASSWORD: mypassword
    NTTMCP_USER: myusername

OR

Use environment variables:

    set +o history
    export NTTMCP_API=api-<geo>.mcp-services.net
    export NTTMCP_API_VERSION=2.10
    export NTTMCP_PASSWORD=mypassword
    export NTTMCP_USER=myusername
    set -o history
