# deploy


## staging

ansible-playbook ansible/site.yml -i ansible/hosts -l staging-art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=master] [-e branch=https://git.linaro.org/people/milosz.wasilewski/art-db-backend.git]]

## production

ansible-playbook ansible/site.yml -i ansible/hosts -l art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=master] [-e repo=https://git.linaro.org/people/milosz.wasilewski/art-db-backend.git]]
