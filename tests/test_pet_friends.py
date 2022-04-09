from api import pf
from settings import \
    valid_email, valid_password, \
    invalid_email, invalid_password, \
    empty_email, empty_password, \
    wrong_email, wrong_password
import os
import pytest


class Tests:
    """Позитивные тесты"""

    # получение api ключа с валидными email и паролем
    @pytest.mark.api
    def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
        # отправка запроса с получением статуса в status и самим ответом в result
        status, result = pf.get_api_key(email, password)
        assert status == 200

        # если ответ не пустой, в нем должен быть словарь с ключом key
        assert 'key' in result

    # получение списка всех питомцев на сайте. filter пуст, т.к. по умолчанию указывается фильтр all_pets
    @pytest.mark.api
    def test_get_all_pet_list_with_valid_key(get_api_key, filter=''):
        # отправка запроса с получением статуса в status и самим ответом в result
        pf.status, result = pf.get_list_of_pets(pf.key, filter)

        # проверяем, что список получен не пустым
        assert len(result['pets']) > 0


# отправка питомца с валидными данными
@pytest.mark.ui
def test_add_new_pet_with_valid_data(get_api_key, name='Феликс', animal_type='без породы', age='9',
                                     pet_photo='image/200px-Domestic_cat.jpg'):
    # автоматическое присвоение фото к pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # отправка питомца с получением статуса в status и самим ответом в result
    pf.status, result = pf.add_new_pet(pf.key, name, animal_type, age, pet_photo)
    assert pf.status == 200

    # проверка наличия имени питомца в ответе после добавления оного
    assert result['name'] == name


# получение списка всех питомцев валидного пользователя.
@pytest.mark.api
def test_get_my_pet_list_with_valid_key(get_api_key, filter='my_pets'):
    # отправка запроса с получением статуса в status и самим ответом в result
    pf.status, result = pf.get_list_of_pets(pf.key, filter)
    assert pf.status == 200

    # проверяем, что список получен не пустым
    assert len(result['pets']) > 0


# обновление информации о существующем питомце
# новые данные
@pytest.mark.ui
def test_successful_update_pet_info(get_api_key, name='Мурзик', animal_type='сфинкс', age='4'):
    # получаем список питомцев пользователя, чтобы убедиться, что там имеются питомцы для обновления
    _, my_pets = pf.get_list_of_pets(pf.key, 'my_pets')

    # если питомец для обновления имеется - обновляем
    if len(my_pets['pets']) > 0:
        pf.status, result = pf.update_pet_info(pf.key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert pf.status == 200

        # проверяем, совпадают ли имя питомца в нашем тесте и в полученном ответе после обновления
        assert result['name'] == name
    else:
        # если питомцев в списке нет - уведомляем об этом
        raise Exception("There is no my pets")


# удаление питомца
@pytest.mark.ui
def test_successful_self_delete_pet(get_api_key):
    # получаем список питомцев пользователя, чтобы убедиться, что там имеются питомцы для удаления
    _, my_pets = pf.get_list_of_pets(pf.key, 'my_pets')

    # если питомцев в списке нет - добавляем нового
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(pf.key, "Суперкот", "кот", "3", "image/200px-Domestic_cat.jpg")
        _, my_pets = pf.get_list_of_pets(pf.key, 'my_pets')

    # берем иднекс первого питомца в списке и по нему удаяем
    pet_id = my_pets['pets'][0]['id']
    pf.status, _ = pf.delete_pet(pf.key, pet_id)

    # снова запрашиваем список, чтобы убедиться, что в нем нет id питомца, которого мы удалили
    _, my_pets = pf.get_list_of_pets(pf.key, 'my_pets')

    assert pf.status == 200

    # проверка отсутствия удаляемого питомца в списке
    assert pet_id not in my_pets.values()


# добавляем питомца без фотографии
@pytest.mark.ui
def test_create_pet_simple_with_valid_data(get_api_key, name='Барбос', animal_type='овчарка', age='3'):
    # добавляем питомца с записью статуса процедуры в status и самим ответом в result
    pf.status, pf.result = pf.create_pet_simple(pf.key, name, animal_type, age)

    assert pf.status == 200

    # проверяем, совпадают ли имя питомца в нашем тесте и в полученном ответе после добавления
    assert pf.result['name'] == name


# добавление фото к существующему питомцу
@pytest.mark.ui
def test_succsesful_add_pet_photo(get_api_key, pet_photo='image/274px-GermanShep1_wb.jpg'):
    # автоматическое присвоение фото к pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # получаем список питомцев пользователя, из которого "достаем" первого питомца, из которого "достаем" его id
    _, my_pets = pf.get_list_of_pets(pf.key, 'my_pets')
    pet_id = my_pets['pets'][0]['id']

    # добавляем фото используя ключ, id питомца и фото
    pf.status, result = pf.add_pet_photo(pf.key, pet_id, pet_photo)
    assert pf.status == 200

    # удостоверяемся, что значение pet_photo не является пустым
    assert result['pet_photo'] != ''


"""Негативные тесты"""


# получение api ключа с несуществующими в базе данных email и паролем
@pytest.mark.api
def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    # записываем статус операции в status, а тело ответа в result
    status, result = pf.get_api_key(email, password)

    # проверяем запрещение доступа
    assert status == 403


# получение api ключа с пустыми значениями email и пароля
@pytest.mark.api
def test_get_api_key_for_empty_user(email=empty_email, password=empty_password):
    # записываем статус операции в status, а тело ответа в result
    status, result = pf.get_api_key(email, password)

    # проверяем запрещение доступа
    assert status == 403


# получение api ключа только с валидным email
@pytest.mark.api
def test_get_api_key_for_only_email_user(email=valid_email, password=empty_password):
    # записываем статус операции в status, а тело ответа в result
    status, result = pf.get_api_key(email, password)

    # проверяем запрещение доступа
    assert status == 403


# получение api ключа только с валидным паролем
@pytest.mark.api
def test_get_api_key_for_only_password_user(email=empty_email, password=valid_password):
    # записываем статус операции в status, а тело ответа в result
    status, result = pf.get_api_key(email, password)

    # проверяем запрещение доступа
    assert status == 403


# получение api ключа с не валидными email и паролем
@pytest.mark.api
def test_get_api_key_for_wrong_data_user(email=wrong_email, password=wrong_password):
    # записываем статус операции в status, а тело ответа в result
    status, result = pf.get_api_key(email, password)

    # проверяем запрещение доступа
    assert status == 403


# получение списка питомцев с не валидным api ключом
@pytest.mark.api
def test_get_list_of_pet_with_invalid_key(filter=''):
    # избегаем выпадения ошибки
    try:
        # записываем статус операции в status, а тело ответа в result
        status, result = pf.get_list_of_pets('89w45v0w4h', filter)

    # ловим ошибку и сообщаем о неправильном api ключе
    except TypeError:
        print('Wrong api key')


@pytest.mark.xfail
# получаем список питомцев с несуществующим фильтром
@pytest.mark.api
def test_get_list_of_pet_with_invalid_filter(get_api_key, filter='wrong_filter'):
    # отправка запроса с получением статуса в status и самим ответом в result
    pf.status, result = pf.get_list_of_pets(pf.key, filter)

    assert pf.status == 400
    assert isinstance(pytest.mark.xfail, int)


@pytest.mark.xfail
# добавляем питомца без данных (кроме фото)
@pytest.mark.ui
def test_add_new_pet_with_empty_data(get_api_key, name='', animal_type='', age='',
                                     pet_photo='image/200px-Domestic_cat.jpg'):
    # автоматическое присвоение фото к pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # записываем статус операции в status, а тело ответа в result
    pf.status, result = pf.add_new_pet(pf.key, name, animal_type, age, pet_photo)

    # ожидаем ошибки (т.к. добвление питомца через UI не позволяет оставлять данные питомца пустыми)
    assert pf.status == 400
    assert isinstance(pytest.mark.xfail, int)


# удаление несуществующего питомца
@pytest.mark.xfail
@pytest.mark.ui
def test_self_delete_nonexisten_pet(get_api_key):
    # сохраняем статус и содержание списка до удаления
    before_delete = pf.get_list_of_pets(pf.key, 'my_pets')

    # записываем статус операции в status
    pf.status, _ = pf.delete_pet(pf.key, '89w45v0w4h')

    # сохраняем статус и содержвания списка после удаления
    after_delete = pf.get_list_of_pets(pf.key, 'my_pets')

    # ожидаем ошибки, т.к. невозможно удалить несуществующего питомца
    assert pf.status == 400
    assert isinstance(pytest.mark.xfail, int)

    # сравниваем списки до и после удаления, т.к. удаления не было - они должны быть равны
    assert after_delete == before_delete


# обновление информации несуществующего питомца
@pytest.mark.xfail
@pytest.mark.ui
def test_update_nonexisten_pet_info(get_api_key, name='Мурзик', animal_type='сфинкс', age='4'):
    # сохраняем статус и содержание списка до обновления
    before_update = pf.get_list_of_pets(pf.key, 'my_pets')

    # записываем статус операции в status, а тело ответа в result
    pf.status, result = pf.update_pet_info(pf.key, '89w45v0w4h', name, animal_type, age)

    # сохраняем статус и содержание списка после обновления
    after_update = pf.get_list_of_pets(pf.key, 'my_pets')

    # ожидаем ошибки, т.к. невозможно обновить данные несуществующего питомца
    assert pf.status == 400
    assert isinstance(pytest.mark.xfail, int)

    # сравниваем списки до и после обновления, т.к. обновления не было - они должны быть равны
    assert after_update == before_update


# добавляем фото к несуществующему питомцу
@pytest.mark.skip
@pytest.mark.ui
def test_add_photo_to_nonexisten_pet(get_api_key, pet_photo='image/274px-GermanShep1_wb.jpg'):
    # автоматическое присвоение фото к pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # получаем список питомцев пользователя, из которого проверим, что не валидного pet_id действительно там нет
    _, my_pets = pf.get_list_of_pets(pf.key, 'my_pets')

    # отправляем фото к несуществующему питомцу с id '89w45v0w4h'. Записываем статус операции в status, а тело ответа
    # в result
    pf.status, result = pf.add_pet_photo(pf.key, '89w45v0w4h', pet_photo)

    # проверяем, что указанного id питомца нет в списке питомцев пользователя
    assert '89w45v0w4h' not in my_pets

    # ожидаем ошибки, т.к. невозможно добавить фото к несуществующему питомцу
    assert pf.status == 400
    assert isinstance(pytest.mark.xfail, int)
