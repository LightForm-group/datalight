.. _prerequisites:

##############
Pre-requisites
##############

To be able to use the *datalight* software you must create an account with
a data repository as an inital step. The steps for registering with supported
data repositories are outlined below.

Zenodo
=======

.. _reqzenodo:

The first step to be able to upload data to Zenodo is to create an account.
This should be done through the Zenodo website.


Account Creation
=================

Open your browser and go to the `zenodo webpage <https://zenodo.org>`_
If you do not already have a Zenodo account click on the **sign up**
button:

It is possible to create a Zenodo account or to log in using your existing 
Github or ORCID accounts.

.. image:: _static/zenodo-signup2.png
    :width: 50 %
    :align: center
    
When you have registered or if you already have a Zenodo account, you 
can log in to your account by clicking on the **log in** button from the home page:

.. image:: _static/zenodo-login.png
    :scale: 100 %
    :align: center
    
This will take you to the log in page where you should input your account details.

.. image:: _static/zenodo-login2.png
    :width: 40 %
    :align: center

One you are logged in, your main account settings can be accessed by the 
bbutton in the top right of the screen (red rectangle):

.. image:: _static/zenodo-logon.png
    :width: 50 %
    :align: center

    
To be able to use datalight you need to create a personal token to
allow datalight to authenticate with the website. This will prevent 
you from having to log into the website each time you use datalight.

.. warning::
   The token created is personal and **should** not be shared with
   anybody. Anyone who has access to this token can publish data 
   to Zenodo under your name.

To create an authentication token, click on the small arrow next to
your login name (red square). A menu will open with different
options. Click on the **Applications** (uderlied in red).

.. image:: _static/zenodo-logon2.png
    :width: 50 %
    :align: center

That will open a new page were you can create a new token by clicking
on the **New token** button (red square):

.. image:: _static/zenodo-token1.png
    :width: 50 %
    :align: center

You have to give a name to the token (e.g. *ZenodoToken*), you can
also choose which action can be done using that token:

- **deposit:action**  Allows the publication of uploaded data
- **deposit:write**  Allows the uploads of metadata and files but not publication of the record.
- **user:email** which allows in read-only mode the access to the
  uploaders email.

To use *datalight* you should check the **deposit:action** and 
**deposit:write** options.

.. image:: _static/zenodo-token2.png
    :width: 50 %
    :align: center

By clicking the button **Create**, Zenodo will create a token which is
an alphanumerical lists of characters:

.. image:: _static/zenodo-token3.png
    :width: 50 %
    :align: center


.. warning::
    This token will be displayed only **once** so save the token to datalight as 
    soon as you create it.
    
Adding the token to datalight
==============================

Datalight reads your access token from a file in the root directory of the datalight program.
Create a new text file called datalight.config in the root directory of datalight.
The token should be stored as follows::

    [zenodo.org]
    token = <token_goes_here>

where you put your user token after the equals sign.

Zenodo Sandbox
===============

To test new code or practice using datalight, there is a Zenodo sandbox website.
This works in exactly the same way as Zenodo but the records there are periodically deleted.
Registration on zenodo sandbox is separate from the main zenodo site but works in the same way.
A zenodo sandbox token can be added to the datalight.config file in the format::

    [sandbox.zenodo.org]
    token = <token_goes_here>