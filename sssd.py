#!/usr/bin/python3





#"the default" - ansible class import (https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
from __future__ import (absolute_import, division, print_function)


#"the default" - ansible class import (https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
from ansible.module_utils.basic import AnsibleModule



import subprocess
import os
#import shutil

#"the default" - ansible class import (https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
__metaclass__ = type

#"the default" - ansible class import (https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
DOCUMENTATION = r'''
---
module: sssd

short_description: This is my module to manage sssd

version_added: "1.0.0"

description: This is my module to manage sssd. ONLY PYTHON3 REMOTE HOST INTERPRETER IS AVAILABLE! works ONLY WHEN you set in the  local ansible.cfg an "interpreter = python3" OR set var "ansible_python_interpreter: python3" in the play/role

author:
    - Alexander Leontev
    - somebody_else
'''

EXAMPLES = r'''
# Pass in a message
- name: add a single domain group
  sssd:
    domain_group: lalalagroup
    group_state: present
# Add a single group - same as a: `realm permit -g domain_group`

- name: add a single domain group
  sssd:
    domain_group: lalalagroup
    group_state: absent
# remove a single group - same as a: `realm deny -g domain_group`

- name: add a multiple domain group (NOT IMPLEMENTED YET)
  sssd:
    domain_group: lalalagroup pupupugroup
    group_state: present
# Add a multiple domain groups - same as a: `realm permit -g domain_group1 domain_group2`

- name: add a multiple domain group (NOT IMPLEMENTED YET)
  sssd:
    domain_group: lalalagroup pupupugroup
    group_state: absent
# remove a multiple groups  - same as a: `realm deny -g domain_group1 domain_group2`

- name: create default sssd config 
  sssd:
    place_default_config: True
# create default sssd config (NOT IMPLEMENTED YET. I do not know what command to use)

- name: join server to an active directory domain (NOT IMPLEMENTED YET)
  sssd:
    in_domain: present
    domain_name: example.com
    admin_user: 
    admin_password: 
    computer_ou: 
# join server to an active directory domain `echo '{{ admin_password }}' | realm join --computer-ou='{{ sssd_ou }}' --verbose example.com -U '{{ admin_user }}'`


- name: remove server from an active directory domain  (NOT IMPLEMENTED YET)
  sssd:
    in_domain: absent
    admin_user: 
    admin_password: 
#
# remove server from an active directory domain (will delete an /etc/sssd/sssd.conf and keytab too!!!) - same as a: `realm leave -U {{ admin_user }}`
'''

#function to detect using python2 or python3  if binary "realm" is in  places, described in PATH 
def which(cmd):
    path = os.environ.get('PATH', '')
    for directory in path.split(os.pathsep):
        if not directory:
            continue
        candidate = os.path.join(directory, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


#Let's describe our CLASSes
class AddOrDelGroupClass(object):
    def __init__(self, module):
        global errorvar
        errorvar = None
        try:
            #check if 'realm list' command tell  us NOT any exception
            checkvar = subprocess.Popen(['realm','list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            streamdata = checkvar.communicate()[0]
            rc = checkvar.returncode
            #print(rc)
        except Exception:
            #if any exception occurs (ex. binary not found in the PATH), we will set errorvar = 1
            #print("EXCEPTION!")
            errorvar = 1
            #print(errorvar)
        self.module = module
        self.domain_group = module.params['domain_group']
        self.group_state = module.params['group_state']
        self.isgroupalreadyexists = self.IsGroupAlreadyExistsFunc()
        #print(self.isgroupalreadyexists)

    def IsGroupAlreadyExistsFunc(self):
        #Here we detect if group is added to realm on the server or not
        utilpath = which("realm")
        if utilpath:
            checkargstring = 'realm list | grep permitted-groups'
            listofgroups = subprocess.check_output(checkargstring, shell=True).decode('utf-8').strip().split('\n')
            return listofgroups
        else:
            return "no gr"
        #return

    def ErrorCallFunc1(self):
        #return format have to be "rc, out, err, msg, failed"
        return 2, "", "ERR_ group_state IS NOT defined AS absent or present", "MSG_ group_state IS NOT defined AS absent or present", "fall to failed state"

    def ErrorCallFunc2(self):
        # return format have to be "rc, out, err, msg, failed"
        messages = "during manipulation of domain groups your args group_state and domain_group SHOULD BE DEFINED, and other args SHOULD NOT BE DEFINED"
        return 2, "", "ERR_ %(insertion)s" % {"insertion": messages}, "MSG_ %(insertion)s" % {"insertion": messages}, "fall to failed state"
      
    def AddGroupFunc(self):
      ###the main logic of function is here
      # return format have to be "rc, out, err, msg, failed"
        if errorvar == 1:
            return 2, "", "ERR_ cant find binary realm. sssd SHOULD be installed! you SHOULD use become!", "MSG_", "fall to failed state"
        else:
            #debug print
            #print(errorvar)
            try:
                ###NOT DONE YET! Here should  create a new logic to determine if there are more than one word in self.domain_group (if user trying to pass multiple groups). Now we fall to 'if' in this way BUT WE SHOULD NOT
                #this tell us if group exists
                if any(self.domain_group in item for item in self.isgroupalreadyexists):
                    return 2, "Group %(insertion)s has ALREADY been added to the server" % {"insertion": self.domain_group}, "", "", ""
                else:
                    #this will add a group (we fall here because group is not present)
                    tmpargstring = 'realm permit -g ' + self.domain_group
                    subprocess.check_call(tmpargstring, shell=True)
                    return 0, "Group %(insertion)s now added to the server" % {"insertion": self.domain_group}, "", "", ""
            except subprocess.CalledProcessError:
                return 2, "Group %(insertion)s NOT added to the server" % {"insertion": self.domain_group}, "Something went wrong", "", 1

        #return lalala

    def RemoveGroupFunc(self):
        ###The main logic of function is here
        # return format have to be "rc, out, err, msg, failed"
        if errorvar == 1:
            return 2, "", "ERR_ cant find binary realm. sssd SHOULD be installed! you SHOULD use become!", "MSG_", "fall to failed state"
        else:
            #debug print
            #print(errorvar)
            try:
                ###NOT DONE YET! Here should  create a new logic to determine if there are more than one word in self.domain_group (if user trying to pass multiple groups). Now we fall to 'else' in ths way BUT WE SHOULD NOT
                #this tell us if group exists
                if any(self.domain_group in item for item in self.isgroupalreadyexists):
                    tmpargstring = 'realm deny -g ' + self.domain_group
                    subprocess.check_call(tmpargstring, shell=True)
                    return 0, "Group %(insertion)s successfully removed from the server" % {"insertion": self.domain_group}, "", "", ""
                else:
                    return 2, "Group %(insertion)s not present on the server" % {"insertion": self.domain_group}, "", "", ""
            except Exception:# as e
                return 2, "undefined error while deleting group from the server" % {"insertion": self.domain_group}, "Something went wrong", "", 1
    #            if e :
    #                return 2, "undefined error while deleting group from the server" % {"insertion": self.domain_group}, "Something went wrong", "", 1
    #            elif e :
    #                return 2, "undefined error while deleting group from the server" % {"insertion": self.domain_group}, "Something went wrong", "", 1
    #            else
    #                return 2, "undefined error while deleting group from the server" % {"insertion": self.domain_group}, "Something went wrong", "", 1




class PlaceDefaultConfigClass(object):
    def __init__(self, module):
        self.module = module
        self.place_default_config = module.params['place_default_config']

    def PlaceConfigFunc(selfself):
        ###The main logic of function is here
        # return format have to be "rc, out, err, msg, failed"
        ###here should be a logic to
        ###1) backup existent config
        ###2) place default config
        ###3) restart sssd.service if needed
        print("existent config backuped and new default config placed")
        #return lalala

    def ErrorCallFunc_1(self):
        # return format have to be "rc, out, err, msg, failed"
        messages = "during manipulation of sssd config file your arg place_default_config SHOULD BE DEFINED, and other args SHOULD NOT BE DEFINED"
        return 2, "", "ERR_ %(insertion)s" % {"insertion": messages}, "MSG_ %(insertion)s" % {"insertion": messages}, "fall to failed state"



class JoinOrLeaveDomainClass(object):
    def __init__(self, module):
        self.module = module
        self.in_domain = module.params['in_domain']
        self.admin_user = module.params['admin_user']
        self.admin_password = module.params['admin_password']
        self.computer_ou = module.params['computer_ou']

    def JoinDomainFunc(self):
        ###The main logic of function is here
        # return format have to be "rc, out, err, msg, failed"
        ###here should be a logic to
        ###1) check if we are already in the domain
        ###2) check if domain controller (we can get it from Host_var/Group_var or sssd config) is available
        ###3) join domain if not joined
        print("Joined to domain")
        #return lalala

    def LeaveDomainFunc(self):
        ###The main logic of function is here
        # return format have to be "rc, out, err, msg, failed"
        ###here should be a logic to
        ###1) check if we are already in the domain
        ###2) leave domain if  joined
        print("Removed from domain")
        #return lalala



def main():

    module_args = {
        "name": {"type": "str", "required": False},
        "domain_group": {"type": "str", "required": False},
        "group_state": {"type": "str", "required": False},
        "place_default_config": {"type": "bool", "required": False, "default": "False"},
        "in_domain": {"type": "str", "required": False},
        "admin_user": {"type": "str", "required": False},
        "admin_password": {"type": "str", "required": False},
        "computer_ou": {"type": "str", "required": False},
    }

    #"the default" - ansible class import (https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    #"the default" - ansible class import (https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
    #We will not use it ()
    #if module.check_mode:
    #    module.exit_json(**result)


    rc = None
    out = ''
    err = ''
    msg = None
    failed = None

    result = {}

    #Get args passed to the module by user/play/role
    flag_group_state = module.params['group_state']
    flag_domain_group = module.params['domain_group']
    flag_place_default_config = module.params['place_default_config']
    flag_in_domain = module.params['in_domain']
    flag_admin_user = module.params['admin_user']
    flag_admin_password = module.params['admin_password']
    flag_computer_ou = module.params['computer_ou']



    #initialize our own CLASSes
    #The "__init__" function of each class will start automatically when we initialize each class
    GroupClassCall = AddOrDelGroupClass(module)
    DefaultconfigClassCall = PlaceDefaultConfigClass(module)
    DomainClassCall = JoinOrLeaveDomainClass(module)





    ###THE MAIN LOGIC BLOCK BEGINS HERE###

    ###we can ONLY use flag_in_domain and flag_admin_user and flag_admin_password and flag_computer_ou separately from all other flags
    ###if it is - let our logic run
    if (
        flag_domain_group is None and
        flag_group_state is None and
        flag_place_default_config is False and
        flag_in_domain is not None and
        flag_admin_user is not None and
        flag_admin_password is not None and
        flag_computer_ou is not None):
        if module.params['in_domain'] == 'present':
            print("try to call JoinDomainFunc here")
            rc, out, err, msg, failed = DomainClassCall.JoinDomainFunc()
        elif module.params['in_domain'] == 'absent':
            print("try to call LeaveDomainFunc here")
            rc, out, err, msg, failed = DomainClassCall.LeaveDomainFunc()
        else:
            print('in_domain IS NOT defined AS absent or present')
        #else:
            #print('during manipulation of the state of presence in a domain group your args "in_domain" and "admin_user" and "admin_password" and "computer_ou" SHOULD BE DEFINED, and other args SHOULD NOT BE DEFINED ')


    ###we can ONLY use flag_place_default_config separately from all other flags
    ###if it is - let our logic run
    if (
        flag_domain_group is None and
        flag_group_state is None and
        flag_place_default_config is not False and
        flag_in_domain is None and
        flag_admin_user is None and
        flag_admin_password is None and
        flag_computer_ou is None):
        if module.params['place_default_config'] == 'True':
            print("try to call PlaceConfigFunc here")
            rc, out, err, msg, failed = DefaultconfigClassCall.PlaceConfigFunc()
        elif module.params['place_default_config'] == 'False':
            print("You can use only place_default_config=True")
        else:
            print("place_default_config IS NOT defined AS True or False")
    #else:
        #print('#during manipulation of sssd config file your arg "place_default_config" should BE DEFINED, and other args SHOULD NOT BE DEFINED')
        #print(flag_place_default_config)
        #rc, out, err, msg, failed = DefaultconfigClassCall.ErrorCallFunc_1()


    ###we can ONLY use flag_domain_group and flag_group_state separately from all other flags
    ###if it is - let our logic run
    if (
        flag_domain_group is not None and
        flag_group_state is not None and
        flag_place_default_config is False and
        flag_in_domain is None and
        flag_admin_user is None and
        flag_admin_password is None and
        flag_computer_ou is None):
        if module.params['group_state'] == 'present':
            #print("try to call AddGroupFunc here")
            rc, out, err, msg, failed = GroupClassCall.AddGroupFunc()
        elif module.params['group_state'] == 'absent':
            #print("try to call RemoveGroupFunc here")
            rc, out, err, msg, failed = GroupClassCall.RemoveGroupFunc()
        else:
            #print('group_state IS NOT defined AS absent or present')
            rc, out, err, msg, failed = GroupClassCall.ErrorCallFunc1()
    #else:
        #print('#during manipulation of domain groups your arg "group_state" and "domain_group" SHOULD  BE DEFINED, and other args SHOULD NOT BE DEFINED')
        #rc, out, err, msg, failed = GroupClassCall.ErrorCallFunc2()

    # Here are standard things "rc, out, err, msg, failed" described. Ansible uses some of this things to determine if we are FAILD or SUCESS or CHANGED.
    # ansible framework status FAILED  needs simultaneously: "result['err']" defined as string and "result['msg']" defined as string and "result['changed'] = False" and "result['failed'] = True"
    # ansible framework status CHANGED needs simultaneously: "result['changed'] = True" and  "result['stdout']" defined as string and "result['stderr'] = None"
    # ansible framework status SUCESS  needs simultaneously: "result['changed'] = False" and "result['stdout']" defined as string
    if rc is None:
        result['changed'] = False
    elif rc == 2:
        result['changed'] = False
    else:
        result['changed'] = True

    if out:
        result['stdout'] = out

    if err:
        result['stderr'] = err

    if msg:
        result['msg'] = msg

    if failed:
        result['failed'] = True

    ###THE MAIN LOGIC BLOCK ENDS HERE###
    module.exit_json(**result)


if __name__ == '__main__':
    main()