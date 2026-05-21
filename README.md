# This is an sssd module for ansible

#### This module developed  with:
### https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

#### Here you can read  how to code your project to make it able to run on the target host with Python2 or Python3: 
### https://docs.ansible.com/ansible/latest/dev_guide/developing_python_3.html#developing-python-3

### Usage:
1. NECESSARY! First of all the package sssd should be installed and configured on the target server (remote host)
2. NECESSARY! Create dir named "library" in your project and place sssd.py there
3. Run your play




### Debugging:
#### Local debugging:
connect to managed server with ssh, switch to user root
install package ansible
install package `sssd` and configure /etc/sssd/sssd.conf 
check groups already added to realm using `realm list | grep -i permitted-gr`
clone project and step to project folder
add new group with this module using `python3 sssd.py example/jsonfile_for_localcheck-addgrp.json`
check groups already added to realm using `realm list | grep -i permitted-gr`

#### Remote-host debugging:
Run this module in ad-hoc mode, for example:
```
ANSIBLE_LIBRARY=./library ansible -i /path/to/inventory_file servername1 -m sssd -a 'domain_group=lalalagroup group_state=present' -b
```




#### Example /etc/sssd/sssd.conf for TESTS:
```
[sssd]
domains = example.comm
config_file_version = 2
reconnection_retries = 3
sbus_timeout = 30

[domain/example.comm]
ad_server = servername.example.comm
ad_domain = example.comm
krb5_realm = example.comm
realmd_tags = manages-system joined-with-adcli
cache_credentials = True
id_provider = ad
ad_enabled_domains = example.comm
krb5_validate = False
krb5_store_password_if_offline = True
krb5_ccachedir = /var/tmp
default_shell = /bin/bash
ldap_id_mapping = True
use_fully_qualified_names = True
fallback_homedir = /home/%d/%u
access_provider = simple
ignore_group_members = True
subdomain_inherit = ignore_group_members
timeout = 300
simple_allow_groups = testgroup1, testgroup2
```








### EXAMPLE of Local debugging
```commandline
19:03:37 fill-VirtualBox sssd_module_for_ansible$ ansible --version
ansible [core 2.16.3]
  config file = /app/pycharm_projects/sssd_module_for_ansible/ansible.cfg
  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python3/dist-packages/ansible
  ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/bin/ansible
  python version = 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] (/usr/bin/python3)
  jinja version = 3.1.2
  libyaml = True
19:04:02 fill-VirtualBox sssd_module_for_ansible$ python3 --version
Python 3.12.3
19:04:12 fill-VirtualBox sssd_module_for_ansible$ uname -rv
6.14.0-29-generic #29~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Aug 14 16:52:50 UTC 2
19:04:14 fill-VirtualBox sssd_module_for_ansible$
19:05:53 fill-VirtualBox sssd_module_for_ansible$ id
uid=0(root) gid=0(root) groups=0(root)
19:05:56 fill-VirtualBox sssd_module_for_ansible$ realm list | grep -i permitted-gr
  permitted-groups: testgroup1, testgroup2
19:06:17 fill-VirtualBox sssd_module_for_ansible$ cat example/jsonfile_for_localcheck-addgrp.json
{
    "ANSIBLE_MODULE_ARGS": {
        "domain_group": "lalalalalalalagroup",
        "group_state": "present"
    }
}
19:06:19 fill-VirtualBox sssd_module_for_ansible$ python3 sssd.py example/jsonfile_for_localcheck-addgrp.json

{"changed": true, "stdout": "Group lalalalalalalagroup now added to the server", "invocation": {"module_args": {"domain_group": "lalalalalalalagroup", "group_state": "present", "place_default_config": false, "name": null, "in_domain": null, "admin_user": null, "admin_password": null, "computer_ou": null}}, "warnings": ["Module did not set no_log for admin_password"]}
19:06:38 fill-VirtualBox sssd_module_for_ansible$ 
19:06:41 fill-VirtualBox sssd_module_for_ansible$ realm list | grep -i permitted-gr
  permitted-groups: testgroup1, testgroup2, lalalalalalalagroup
19:06:50 fill-VirtualBox sssd_module_for_ansible$ 
19:08:21 fill-VirtualBox sssd_module_for_ansible$ cat example/jsonfile_for_localcheck-delgrp.json 
{
    "ANSIBLE_MODULE_ARGS": {
        "domain_group": "lalalalalalalagroup",
        "group_state": "absent"
    }
}
19:08:26 fill-VirtualBox sssd_module_for_ansible$ python3 sssd.py example/jsonfile_for_localcheck-delgrp.json
realm: Specifying deny without --all is deprecated. Use realm permit --withdraw

{"changed": true, "stdout": "Group lalalalalalalagroup successfully removed from the server", "invocation": {"module_args": {"domain_group": "lalalalalalalagroup", "group_state": "absent", "place_default_config": false, "name": null, "in_domain": null, "admin_user": null, "admin_password": null, "computer_ou": null}}, "warnings": ["Module did not set no_log for admin_password"]}
19:08:42 fill-VirtualBox sssd_module_for_ansible$ realm list | grep -i permitted-gr
  permitted-groups: testgroup1, testgroup2
19:08:45 fill-VirtualBox sssd_module_for_ansible$ 
```

### TODO
- PlaceDefaultConfigClass not implemented yet
- JoinOrLeaveDomainClass not implemented yet
- AddOrDelGroupClass cant handle blank stdout of 'realm list' (when "server is not added to a domain" = "empty /etc/sssd/sssd.conf" ) -> 'realm permit -g somegroup' returns rc=1 and stdout "realm: Couldn't find a configured realm"
- (solved) AddOrDelGroupClass cant work with python2 remote-host interpreter because of usage imported 'shutil' (which can serve with python3 only)
- AddOrDelGroupClass cant handle multiple groups pass 
- AddOrDelGroupClass cant handle invalid symbols (when you pass only a comma to domain_group like this `domain_group=,`)
- AddOrDelGroupClass cant handle exception when you pass empty var domain_group like this  `domain_group=`
- (solved) ansible.module_utils.basic import error if interpreter is python2 (when you use  Local debugging)
- something else. I forgot ¯\_(ツ)_/¯


### known bugs
```bash

```