# ART

## development

Make sure that you have all requirements.txt from `requirements-dev.txt`.

To start all development processes 
```
honcho start
```

## deploy

* default branch for deployment `master`
* default repository for deployment `https://git.linaro.org/people/milosz.wasilewski/art-db-backend.git`

Those can be changed with `-e` option

### staging

```bash
ansible-playbook ansible/site.yml -i ansible/hosts -l staging-art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=oter-branch] [-e repo=other-repo]]
```

### production

```bash
ansible-playbook ansible/site.yml -i ansible/hosts -l art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=oter-branch] [-e repo=other-repo]]
```
