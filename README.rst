=====================
XtremIO Python Module
=====================


Note that this module is still a work-in-progress and not ready for production use...



Connecting to the Array
-----------------------

The first step obviously is to import the "xtremio" module :

.. code-block:: python

    >>> import xtremio


Then connect to the XMS, providing the XMS name, username and password :

.. code-block:: python

    >>> x = xtremio.XtremIO("xms.example.com", "admin", "Xtrem10")


If using a multi-cluster environment (ie, one XMS managing multiple arrays) then
you will need to specify the array in order for any array-level commands to work :

.. code-block:: python

    >>> x.set_cluster("mycluster")

The cluster selection can be cleared by running the same command with no options.


Commands
--------

Most commands follow a common format of action_object().  eg, to create a volume the
command is create_volume().  To remove a snapshots it's remove_snapshot(), and so on.

Object Types
------------

The object types currently supported are :

-  volume
-  ig                  (Initiator Group)
-  initiator 
-  volume_mapping
-  cg                  (Consistency Group)
-  snapshot
-  snapshot_set
-  cluster


Get Commands
------------

"get" commands function the same for all objects.  To get a list of all of an object type, use get_XXXs() with an "s" on the end
of the command, where XXX is the object type.  eg, to get a list of all volumes, use get_volumes() :

.. code-block:: python

    >>> x.get_volumes()
    [{u'index': 1, u'name': u'ScottH-DS', u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/volumes/1', u'sys-name': u'mycluster', u'vol-size': u'1073741824', u'guid': u'b515b55e44ef4ce8a0f090ecb598f6a1'}, {u'index': 2, u'name': u'MyDS', u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/volumes/2', u'sys-name': u'mycluster', u'vol-size': u'2147483648', u'guid': u'129a9b43ea494049a19698d13646daca'},

By default, only a small number of attributes for each object are returned, however you can also pass a list of additional
attributes to be returned :

.. code-block:: python

    >>> x.get_volumes(['management-locked','lb-size'])

To get full details on an individual object, use get_XXX() (without the "s"), passing in either the name or index for the specific entiry. eg :

.. code-block:: python

    >>> x.get_volume("myvol1")
    {u'small-io-alerts': u'disabled', u'last-refreshed-from-obj-name': None, u'obj-severity': u'information', u'rd-bw': u'0', [...etc...]
    >>> x.get_volume(1056)['vol-size']
    u'104857600'


Create Commands
---------------

Create commands vary slightly as they take different options depending on the object type, but are generally similar.

All create commands take the object name as the first option, followed by options relevant to whatever is being created.

eg, a volume requires the size, passed as either a string or an integer in KB. The following will both create a 10GB volume

.. code-block:: python

    >>> x.create_volume('MyVol1', '10G');
    {u'index': 1057, u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/volumes/1057', u'rel': u'self'}
    >>> x.create_volume('MyVol2', 10*1024*1024);
    {u'index': 1058, u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/volumes/1058', u'rel': u'self'}

Creating an initiator group accepts only a name :

.. code-block:: python

    >>> x.create_ig("myIG1")

whilst an initiator requires the IG it's to be in, the port address (WWN or iSCSI) and the OS type (one of solaris, aix, windows, esx, linux, hpux or other) :

.. code-block:: python

    >>> x.create_initiator("myinit1", "myIG1", "11:11:22:22:33:33:44:44", "linux")
    {u'index': 36, u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/initiators/36', u'rel': u'self'}

Creating a CG (Consistency Group) requires a list of volumes :

.. code-block:: python

    >>> x.create_cg('MyCG', ['MyVol1','MyVol2'])
    {u'index': 3, u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/consistency-groups/3', u'rel': u'self'}

Creating a snapshot is different as it uses named arguments.  The source of the snapshot can be any of a Consistency Group (cg=xxx), a
Snapshot Set (ss=xxx) or a Volume (vol=xxx). You can also spceify the resulting snapshots set name (ssname=xxx), the volume suffix
appended to the snapshots (suffix=xxx) and whether you want a readonly snapshot or not (readonly=True/False, default is false for read-write) :

.. code-block:: python

    >>> x.create_snapshot(cg='MyCG', ssname='MySnapSet1', suffix='snap1', readonly=True)
    {u'index': 1059, u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/snapshots/1059', u'rel': u'self'}


Remove Commands
---------------

"remove" commands also function the same for all object types. 

To move an object, call the remove function passing either the object name or it's index.  eg :

.. code-block:: python

    >>> x.remove_volume(1056)


Modify Commands
---------------

Similar to Create, the Modify commands accept varying options relevant to the object.  Generally only a single item can be modified at once.

Volume and Snapshot :

- name
- size

IG :

- name
- os  (modifies the os of all initiators in the IG)

Initiator :

- name
- address
- os

Snapshot Set and CG :

- name

A CG can also have volumes added to it or removed from it using the "add=" and "remove=" options.


eg, rename and resize a volume :

.. code-block:: python

    >>> x.modify_volume("mynewvol1", name="myvol1")
    >>> x.modify_volume("myvol1", size='200g')

Change the OS on all initiators in an IG :

.. code-block:: python

    >>> x.modify_ig("myIG1", os="aix")

Add a volume to an existing Consistency Group :

.. code-block:: python

    >>> x.modify_cg('MyCG', add='MyVol3')
    {u'index': 3, u'href': u'https://xtremio4.scxtremiolab.com/api/json/v2/types/consistency-group-volumes/3', u'rel': u'self'}

