from fastapi import APIRouter, Depends, HTTPException, status, Body
from models.user import UserForm, User, UsersResponseList, UserName, UserChangePassword, UserChangeEmail, UserByToken, Role, UserList
from models.generic import GenericDevice, OnlyGenericName, DevicesNames
from beanie import PydanticObjectId
from utils.password import verify_password, get_password_hash
from beanie.operators import NotIn
from typing import Annotated
from routers.auth import get_current_admin_user, get_current_user
from models.filters import FiltersPayload, FilterMode
from beanie.operators import And, RegEx, Or
from pymongo import DESCENDING, ASCENDING
import os
from dotenv import load_dotenv

users_router = APIRouter(
    prefix="/users",
    tags=["users"],)


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

#@users_router.get("/user")
#async def hello_world():
#    x = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
#    return {"Hello": "World"}



#@users_router.get('/list', status_code=status.HTTP_200_OK, response_model=list[ShowUser])
#async def get_users(current_admin: Annotated[UserByToken, Depends(get_current_admin_user)], skip: int = 0, limit: int = 10):
#    users = await User.find(skip=skip, limit=limit).project(ShowUser).to_list()
#    return users




async def create_initial_admin():

    admin_exists = await User.find_one(User.role == Role.admin)

    if not admin_exists:
        admin_user = User(
            email=ADMIN_EMAIL,
            full_name="admin", 
            role=Role.admin,
        )
        await admin_user.create()
    else:
        pass

@users_router.post('/list', status_code=status.HTTP_200_OK, response_model=UsersResponseList)
async def get_users(
    current_admin: Annotated[UserByToken, Depends(get_current_admin_user)],
    filters_payload: Annotated[FiltersPayload, Body()]
):

    filters = filters_payload.columnFilters
    filterModes = filters_payload.columnFilterFns
    sorting = filters_payload.sorting
    globalFilter = filters_payload.globalFilter
    skip = filters_payload.pagination.pageIndex * filters_payload.pagination.pageSize
    limit = filters_payload.pagination.pageSize


    valid_fields = {
        'email', 'full_name', 'role', 'active', 'createdAt', 'updatedAt'
    }

    partial_filters = []
    for col_filter in filters:
        field = col_filter.id  
        val = col_filter.value 
        if field not in valid_fields or not val:
            continue

        mode = filterModes.get(field, FilterMode.contains)  

        
        if mode == FilterMode.contains:
            partial_filters.append(RegEx(getattr(User, field), f".*{val}.*", options="i"))
        elif mode == FilterMode.startsWith:
            partial_filters.append(RegEx(getattr(User, field), f"^{val}", options="i"))
        elif mode == FilterMode.endsWith:
            partial_filters.append(RegEx(getattr(User, field), f"{val}$", options="i"))

    
    if partial_filters:
        query = And(*partial_filters)
    else:
        query = None

    
    if globalFilter:
        gf = globalFilter
        global_filters = [
            RegEx(getattr(User, field), f".*{gf}.*", options="i")
            for field in ['email', 'full_name', 'role']
        ]
        if query:
            query = And(query, Or(*global_filters))  
        else:
            query = Or(*global_filters)  


    
    sort_params = []
    for sort in sorting:
        field = sort.get('id')  
        if field not in valid_fields:
            continue
        if sort.get('desc'):
            sort_params.append((getattr(User, field), DESCENDING))
        else:
            sort_params.append((getattr(User, field), ASCENDING))

    
    find_query = User.find(query) if query else User.find()
    if sort_params:
        find_query = find_query.sort(*sort_params)

    print(skip)
    print(limit)

    total = await find_query.count()
    users = await find_query.skip(skip).limit(limit).to_list()

    
    users_response = []
    for user in users:
        data = user.model_dump() 
        devices = data.get("devices") or []
        data["devices"] = devices
        users_response.append(UserList(**data))

    return UsersResponseList(data=users_response, totalRowCount=total)





#@users_router.get('/{user_id}', status_code=status.HTTP_200_OK, response_model= ShowUser)
#async def get_user(user_id: PydanticObjectId, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):
#    user = await User.get(user_id)
#
#    if user is None:
#        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")

#    return user


@users_router.put('/{user_id}', status_code=status.HTTP_200_OK)
async def update_user(user_id: PydanticObjectId, user_data: UserForm, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):
    
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
    
    if user_id != current_admin.id and user.role == Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se puede modificar otro usuario administrador")


    if user_data.email != user.email or user_data.full_name != user.full_name or user_data.role != user.role:

        user_exist = await User.by_email(user_data.email)

        if user_exist and user_id != user_exist.id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Correo electronico no disponible")

        user.email = user_data.email
        user.full_name = user_data.full_name
        user.role = user_data.role
        await user.replace()
        return {"message": "Usuario actualizado"}

    return {"message": "No se realizaron cambios. Los datos ya son utilizados por el usuario"}


@users_router.get('/{user_id}/name', status_code=status.HTTP_200_OK)
async def get_full_name(user_id: PydanticObjectId, current_user: Annotated[UserByToken, Depends(get_current_user)]):
    
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo puedes obtener tu propio nombre de usuario")
    
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")

    return user.full_name

@users_router.patch('/{user_id}/name', status_code=status.HTTP_200_OK)
async def update_user_name(user_id: PydanticObjectId, user_data: UserName, current_user: Annotated[UserByToken, Depends(get_current_user)]):
    
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo puedes modificar tu propio nombre de usuario")
    
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
    
    if user_data.full_name != user.full_name:

        user.full_name = user_data.full_name
        await user.replace()
        return {"message": "Full name of modified user"}

    return {"message": "The name has not been changed. It is already being used by the user"}



@users_router.patch('/{user_id}/password', status_code=status.HTTP_200_OK)
async def update_user_password(user_id: PydanticObjectId, user_data: UserChangePassword, current_user: Annotated[UserByToken, Depends(get_current_user)]):
    
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You can only change your own password.")
    
    if user_data.new_password != user_data.new_password_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords must be the same")

    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist.")
    

    if not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password incorrect")
    
    if user_data.new_password == user_data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must update your password to one that is different from your current one.")



    user.password = get_password_hash(user_data.new_password)
    await user.replace()
    return {"message": "Password successfully changed"}


@users_router.patch('/{user_id}/email', status_code=status.HTTP_200_OK)
async def update_user_email(user_id: PydanticObjectId, user_data: UserChangeEmail, current_user: Annotated[UserByToken, Depends(get_current_user)]):
    
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You can only modify your own email address.")
    
    if user_data.new_email != user_data.new_email_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New emails must be identical.")

    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist.")
    
    if user_data.email != user.email:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect current email address")

    if user_data.email == user_data.new_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The new email address must be different from the current one.")

    user_exist = await User.by_email(user_data.new_email)

    if user_exist:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email address not available")


    user.email = user_data.new_email
    await user.replace()
    return {"message": "User's email address changed"}



@users_router.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user(user_id: PydanticObjectId, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist.")
    
    if user_id == current_admin.id or user.role == Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You cannot delete your user or an administrator's user.")
    
    await user.delete()
    return {"message": "User successfully deleted"}


async def get_devices_names_by_user_id(user_id: PydanticObjectId) -> list[str]:
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist.")

    if user.devices:
        return user.devices
    
    return []


@users_router.get('/{user_id}/devices', status_code=status.HTTP_200_OK, response_model=list[str])
async def get_user_devices(user_id: PydanticObjectId, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):

    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist.")
    
    if user_id != current_admin.id and user.role == Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You cannot modify another administrator's devices.")

    if user.devices:
        return user.devices
    
    return []



@users_router.get('/{user_id}/devices/available', status_code=status.HTTP_200_OK, response_model=list[str])
async def get_available_devices(user_id: PydanticObjectId, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist.")
    
    if user_id != current_admin.id and user.role == Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You cannot modify another administrator's devices.")

    if not user.devices:
        devices_available_names = await GenericDevice.find().project(OnlyGenericName).to_list()
        return [device.name for device in devices_available_names]
        
    
    devices_available_names = await GenericDevice.find(NotIn(GenericDevice.name, user.devices)).project(OnlyGenericName).to_list()
    return [device.name for device in devices_available_names]

@users_router.patch('/{user_id}/devices', status_code=status.HTTP_200_OK)
async def update_user_devices(user_id: PydanticObjectId, payload: DevicesNames, current_admin: Annotated[UserByToken, Depends(get_current_admin_user)]):
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist.")
    
    if user_id != current_admin.id and user.role == Role.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You cannot modify another administrator's devices.")

    device_names = await GenericDevice.find().project(OnlyGenericName).to_list()
    valid_device_names = set(device.name for device in device_names)

    for name in payload.names:
        if name not in valid_device_names:   
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more devices do not exist."
            )

    user.devices = payload.names
    await user.replace()

    return {"message": "User devices successfully updated"}
    