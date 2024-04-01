import os
from fastapi import File, UploadFile, Depends, Form
from sqlalchemy.orm import Session

from . import tdd_router
from project.config import settings
from project.database import get_db_session
from project.tdd.models import Member
from project.tdd.tasks import generate_avatar_thumbnail


@tdd_router.post('/member_signup/')
def member_signup(
    username: str = Form(...),
    email: str = Form(...),
    upload_file: UploadFile = File(...),
    session: Session = Depends(get_db_session)
):
    file_location = os.path.join(
        settings.UPLOADS_DEFAULT_DEST,
        upload_file.filename
    )
    with open(file_location, 'wb') as file_object:
        file_object.write(upload_file.file.read())
    try:
        member = Member(
            email=email,
            username=username,
            avatar=upload_file.filename
        )
        session.add(member)
        session.commit()
        member_id = member.id
    except:
        session.rollback()
        raise

    generate_avatar_thumbnail.delay(member_id)
    return {'message': 'Sign up successful'}
