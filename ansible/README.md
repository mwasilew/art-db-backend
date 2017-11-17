# example: deploy to staging

```
./ansible-playbook --ask-become-pass -l staging site.yml
```

# example: deploy to production

```
./ansible-playbook --ask-become-pass -l production site.yml
```

# example: deploy to vagrant

```
NOPROVISION=1 vagrant up
ssh-keygen -f ~/.ssh/known_hosts -R art-reports.local
./ansible-playbook -l local site.yml -u vagrant --private-key ../.vagrant/machines/default/libvirt/private_key
```
