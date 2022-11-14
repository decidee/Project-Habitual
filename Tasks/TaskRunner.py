import os
import asyncio
import json
from dotenv import load_dotenv

from telethon import TelegramClient, errors, functions
from telethon.sessions import StringSession


from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine

from fastapi import FastAPI, status
from pydantic import BaseModel

env_dir = os.path.dirname(__file__)
load_dotenv(f"{env_dir}/.env")

import logging
logging.basicConfig(filename=__name__, filemode='a', format='[%(levelname) 5s/%(asctime)s] Func - %(funcName)s : %(name)s: %(message)s',
                    level=logging.DEBUG)

app = FastAPI()

db = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'), echo=False)
Base = automap_base()
Base.prepare(db, reflect=True)

Tele = Base.classes.TeleAcc
User = Base.classes.UserAcc

Session = sessionmaker(bind=db)
session = Session()


class UserID(BaseModel):
    UserID: str


async def ClientMaker(C_User):
    UserInfo1 = session.query(Tele).filter_by(OwnerAcc=C_User).first()
    client = TelegramClient(StringSession(UserInfo1.SessionFile), UserInfo1.ApiId, UserInfo1.ApiHash)
    if not client.is_connected():
        await client.connect()
    try:
        await client.is_user_authorized()
        return client
    except Exception:
        logging.exception(f" {C_User} is not authorized - Must be Authorized")


@app.get('/test')
async def hello():
    logging.info('Test')
    return "Api Test"


async def Qrlogger(C_User):
    UserInfo1 = session.query(Tele).filter_by(OwnerAcc=C_User).first()
    if UserInfo1:   
        def display_url_as_qr(url):
            add_on = session.query(Tele).filter_by(OwnerAcc=C_User).update(dict(SignInCode=url))
            session.commit()
            logging.debug(f"QrCode URL for : {C_User} : Generated")
            return

        client = TelegramClient(StringSession(), UserInfo1.ApiId, UserInfo1.ApiHash)
        await client.connect()
        logging.info(f" Client with {C_User} is Connected - {client.is_connected()}")

        if client.is_connected():
            qr_login = await client.qr_login()
            logging.debug(f"QrCode for {C_User} -- will expire in {qr_login.expires}")
            display_url_as_qr(qr_login.url)

            try:
                await qr_login.wait(timeout=30)
                if await client.is_user_authorized():
                    logging.debug(f"USER {C_User} is Authorized")
                    sessionstring = client.session.save()
                    add_on = session.query(Tele).filter_by(OwnerAcc=C_User).update(dict(SessionFile=sessionstring,Auth=True))
                    session.commit() 

            except TimeoutError:
                await qr_login.recreate()
                logging.exception(f"QR Code for {C_User} has been recreated.")
            
            except Exception as e:
                logging.exception("Exception raised on qr_login: %s ", e)


@app.post("/QrLogin", status_code=status.HTTP_201_CREATED)
async def QrLogin(idata:UserID):
    current_user = idata.UserID
    task = asyncio.create_task(Qrlogger(current_user))
    logging.info("NEW : %s", task)
    return "DONE"


async def Sender(C_User):
    try:
        client = await ClientMaker(C_User)
        b = await client.send_message('me', 'What a Message')
    except Exception as e:
        logging.exception(f"Exception {e}")


@app.post("/send", status_code=status.HTTP_201_CREATED)
async def send(idata:UserID):
    current_user = idata.UserID
    task = asyncio.create_task(Sender(current_user))
    logging.debug("NEW : %s", task)
    return "DONE"


async def ClientContact(C_User):
    client = await ClientMaker(C_User)
    contact = await client(functions.contacts.GetContactsRequest(hash=0))
    contacts_json = contact.to_dict()
    contact_list = []
    key_value = ['id','access_hash','first_name','last_name','username','phone','photo']
    for i in contacts_json["users"]:
        w = [v for k,v in i.items() if k in key_value]
        contact_dict = {'id':'','access_hash':'','first_name':'','last_name':'','username':'','phone':'','photo':''}
        contact_dict['id']= w[0]
        contact_dict['access_hash'] = w[1]
        contact_dict['first_name'] = w[2]
        contact_dict['last_name'] = w[3]
        contact_dict['username'] = w[4]
        contact_dict['phone'] = w[5]
        contact_dict['photo'] = str(w[6])
        contact_list.append(contact_dict)

    add_on = session.query(Tele).filter_by(OwnerAcc=C_User).update(dict(Contact=contact_list))
    session.commit() 
    logging.debug(f'Contact Created')
    return


@app.post("/contact", status_code=status.HTTP_201_CREATED)
async def contact(idata:UserID):
    current_user = idata.UserID
    task = asyncio.create_task(ClientContact(current_user))
    return "DONE"

'''
async def contact_takeout(C_User):
    UserInfo1 = session.query(Tele).filter_by(OwnerAcc=C_User).first()
    client = TelegramClient(StringSession(UserInfo1.SessionFile), UserInfo1.ApiId, UserInfo1.ApiHash)
    await client.connect()
    if await client.is_user_authorized():
        logging.debug(f" {C_User} is authorized")
        try:
            async with client.takeout(contacts=True,users=True) as takeout:
                logging.debug(f" {C_User} - Takeout Session")
                contact = await takeout(functions.contacts.GetSavedRequest())
                for k,v in enumerate(contact):
                    pass
                    # (k,v.phone,v.first_name,v.last_name,sep=',')
                    # export contact to vcard file

        except errors.TakeoutInitDelayError as e:
            logging.exception('Must wait', e.seconds, 'before takeout')


@app.post("/ContactTakeout", status_code=status.HTTP_201_CREATED)
async def ContactTakeout(idata:UserID):
    current_user = idata.UserID
    task = asyncio.create_task(contact_takeout(current_user))
    logging.debug("NEW : %s", task)
    return "DONE"
'''