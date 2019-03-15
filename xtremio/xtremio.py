"""

XtremIO library

Version 0.1

Scott Howard
scott.howard@emc.com
"""


import requests
from requests.auth import HTTPBasicAuth
from urllib import quote_plus
import json

class XtremIO(object):

    def __init__(self, xms, username, password, checkcert=True):

        req = requests.get('https://' + xms + '/api/json/v2/types', auth=HTTPBasicAuth(username, password), verify=checkcert)

        if req.ok:
            self._xms = xms
            self._username = username
            self._password = password
            self._httpauth = HTTPBasicAuth(username, password)
            self._checkcert = checkcert
            self._cluster_name = "";
        else:
            try:
                errorresp = json.loads(req.content.decode('utf-8'))
                message = errorresp['message']
            except:
                message = str(req.status_code) + ' ' + req.reason
            raise Exception(message)


    def _request(self, method, uri, body=None):

        req = requests.request(method, 'https://' + self._xms + uri, auth=self._httpauth, verify=self._checkcert, data=json.dumps(body))

        resp = None
        try:
            resp = json.loads(req.content.decode('utf-8'))
        except:
            pass

        if not req.ok:
            try:
                message = resp['message']
                if req.status_code == 400 and method == 'GET' and message == 'obj_not_found':
                    return None
            except:
                message = str(req.status_code) + ' ' + req.reason
            raise Exception(message)
        return(resp)


    def _cluster(self):
        if (self._cluster_name):
            return '&cluster-name' + self._cluster_name
        else:
            return ''


    def _name_or_id(self, id):
        if type(id) == str:
            return('?name=' + quote_plus(id))
        elif type(id) == int:
            if id != -1:
                return('/' + str(id) + "?")
            else:
                return('?')
        else:
            return('?');


    def _get_list(self, otype, prop=None):
        proplist='?'
        if prop:
            proplist='?full=1&prop=' + '&prop='.join(prop)
        return self._request('GET', '/api/json/v2/types/' + otype + proplist + self._cluster())[otype]


    def _get(self, otype, id, value=None):
        resp = self._request('GET', '/api/json/v2/types/' + otype + self._name_or_id(id) + self._cluster())
        try:
            resp = resp['content']
            if value:
                resp = resp[value]
        except:
            resp = None
        return(resp)

    def _create(self, otype, body=None):
        return (self._request('POST', '/api/json/v2/types/' + otype  + self._name_or_id(-1) + self._cluster(), body))['links'][0]

    def _modify(self, otype, id, body=None):
        return self._request('PUT', '/api/json/v2/types/' + otype  + self._name_or_id(id) + self._cluster(), body)

    def _remove(self, otype, id, body=None):
        return self._request('DELETE', '/api/json/v2/types/' + otype  + self._name_or_id(id) + self._cluster(), body)


    def get_volumes(self, prop=None):
        if not prop:
            prop=['name','sys-name','vol-size','guid'];
        return self._get_list('volumes', prop)

    def get_volume(self, id):
        return self._get('volumes', id)

    def create_volume(self, name, size):
        return self._create('volumes', {'vol-name': name, 'vol-size': size})

    def remove_volume(self, id):
        return self._remove('volumes', id)

    def modify_volume(self, id, size=None, name=None):
        if [size, name].count(None) != 1:
            raise Exception("modify_volume requires exactly one of {name, size)")
        if size:
            body={'vol-size': size}
        if name:
            body={'vol-name': name}
        return self._modify('volumes', id, body);


    def create_volume_mapping(self, volume, ig):
        return self._create('lun-maps', {'vol-id': volume, 'ig-id': ig})

    def get_volume_mapping(self, volume, ig):   # XXX Needs to handle volume/ig ID not just name
        lunmap = self._request('GET', '/api/json/v2/types/lun-maps?full=1&filter=vol-name:eq:' + volume + '&filter=ig-name:eq:' + ig + '&cluster-name=' + self._cluster())
        try:
            return lunmap['lun-maps'][0]
        except:
            return None


    def remove_volume_mapping(self, volume, ig):
        mapindex = self.get_volume_mapping(volume, ig)
        if not mapindex:
            raise Exception('volume mapping not found')
        return self._remove('lun-maps', mapindex['index'])


    def get_igs(self, prop=None):
        return self._get_list('initiator-groups', prop)

    def get_ig(self, id):
        return self._get('initiator-groups', id)

    def create_ig(self, name):
        return self._create('initiator-groups', {'ig-name': name})

    def remove_ig(self, id):
        return self._remove('initiator-groups', id)

    def modify_ig(self, id, name=None, os=None):
        if [name, os].count(None) != 1:
            raise Exception("modify_ig requires exactly one of {name, os}")
        if name:
            body={'new-name': name}
        if os:
            body={'operating-system': os}
        return self._request('PUT', '/api/json/v2/types/initiator-groups' + self._name_or_id(id) + self._cluster(), body)



    def get_initiators(self, prop=None):
        return self._get_list('initiators', prop)

    def get_initiator(self, id):
        return self._get('initiators', id)

    def create_initiator(self, name, ig, address, os):
        return self._create('initiators', {'initiator-name': name, 'ig-id': ig, 'port-address': address, 'operating-system': os})

    def remove_initiator(self, id):
        return self._remove('initiators', id)

    def modify_initiator(self, id, name=None, address=None, os=None):
        if [name, address, os].count(None) != 2:
            raise Exception("modify_initiator requires exactly one of {name, address, os}")
        if name:
            body={'initiator-name': name}
        if address:
            body={'port-address': address}
        if os:
            body={'operating-system': os}
        return self._modify('initiators', id, body)


    def get_cgs(self, prop=None):
        return self._get_list('consistency-groups', prop)

    def get_cg(self, id):
        return self._get('consistency-groups', id)

    def create_cg(self, name, vollist=[]):
        return self._create('consistency-groups', {'consistency-group-name': name, 'vol-list': vollist})

    def remove_cg(self, id):
        return self._remove('consistency-groups', id)

    def modify_cg(self, id, name=None, add=None, remove=None):
        if [name, add, remove].count(None) != 2:
            raise Exception("modify_cg requires exactly one of {name, add, remove)")
        if name:
            return self._modify('consistency-groups', id, {'new-name': name})
        if add:
            return self._create('consistency-group-volumes', {'cg-id': id, 'vol-id': add})
        if remove:
            return self._remove('consistency-group-volumes', id, {'vol-id': remove})


    def get_snapshot(self, id):
        return self._get('snapshots', id)

    def create_snapshot(self, cg=None, ss=None, vol=None, ssname=None, suffix=None, readonly=False):
        if [cg, ss, vol].count(None) != 2:
            raise Exception("create_snapshot requires exactly one of {cg, ss, vol)")
        if cg:
            body={'consistency-group-id': cg}
        if ss:
            body={'snapshot-set-id': ss}
        if vol:
            if type(vol) == list:
                body={'volume-list': vol}
            else:
                body={'volume-list': [vol]}

        if ssname:
            body.update({'snapshot-set-name':ssname})
        if suffix:
            body.update({'snap-suffix':suffix})
        if readonly:
            body.update({'snapshot-type': 'readonly'})
        return self._create('snapshots', body);

    def remove_snapshot(self, id):
        return self._remove('snapshots', id)

    def modify_snapshot(self, id, size=None, name=None):
        if [size, name].count(None) != 1:
            raise ValueError("modify_snapshot requires exactly one of {name, size)")
        if size:
            body={'vol-size': size}
        if name:
            body={'vol-name': name}
        return self._modify('snapshots', id, body);

    def refresh_snapshot(self, fromcg=None, fromss=None, fromvol=None, tocg=None, toss=None, tovol=None, nobackup=True, backupsuffix=None, ss=None):
        if [fromcg, fromss, fromvol].count(None) != 2:
            raise ValueError("refresh_snapshot requires exactly one of {fromcg, fromss, fromvol)")
        if [tocg, toss, tovol].count(None) != 2:
            raise ValueError("refresh_snapshot requires exactly one of {tocg, toss, tovol)")
        if type(fromvol) == list:
            raise ValueError("fromvol must be a single volume for refresh")
        body={}
        if fromcg:  body.update({'from-consistency-group-id': fromcg})
        if fromss:  body.update({'from-snapshot-set-id': fromss})
        if fromvol: body.update({'from-volume-id': fromvol})
        if tocg:    body.update({'to-consistency-group-id': tocg})
        if toss:    body.update({'to-snapshot-set-id': toss})
        if tovol:   body.update({'to-volume-id': tovol})
        if ss:      body.update({'snapshot-set-name': ss})
        if nobackup:
            body.update({'no-backup':'true'})
        elif backupsuffix:
            body.update({'backup-snap-suffix':backupsuffix})
        return self._create('snapshots', body)

    def get_snapshot_set(self, id):
        return self._get('snapshot-sets', id)

    def remove_snapshot_set(self, id):
        return self._remove('snapshot-sets', id);

    def modify_snapshot_set(self, id, name):
        return self._modify('snapshot-sets', id, {'new-name': name});

    def get_clusters(self):
        return self._get_list('clusters')

    def get_cluster(self, id):
        return self._get('clusters', id)

    def set_cluster(self, cluster=None):
        if cluster:
            self.get_cluster(cluster)
        self._cluster_name=cluster

