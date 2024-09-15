from httpx import AsyncClient


async def test_redirect(ac: AsyncClient):
    """
    Тест редиректа: успешный
    """

    response = await ac.get('/redirect/3e2be2ac-8771-4923-bbad-125940a6d9df')

    assert response.status_code == 307


async def test_redirect_label_not_found(ac: AsyncClient):
    """
    Тест редиректа: не найден ссылка по label
    """

    response = await ac.get('/redirect/123133213')

    assert response.status_code == 404
    assert 'Нужная вам ссылка для оплаты не найдена' in response.text


async def test_redirect_payment_completed(ac: AsyncClient):
    """
    Тест редиректа: уже оплачено
    """

    response = await ac.get('/redirect/69f35136-fdfb-44c6-b6af-2a20d5d281f7')

    assert response.status_code == 400
    assert 'Оплата уже произведена' in response.text


async def test_redirect_outdated_request(ac: AsyncClient):
    """
    Тест редиректа: время истекло
    """

    response = await ac.get('/redirect/3081c856-f0de-4047-b8d7-f10ad1b0faf0')

    assert response.status_code == 400
    assert 'Время на оплату истекло' in response.text


async def test_redirect_newer_url_exists(ac: AsyncClient):
    """
    Тест редиректа: существует более новая ссылка
    """

    response = await ac.get('/redirect/c9dd753a-1efb-452d-8d3f-a5ec3233ee00')

    assert response.status_code == 400
    assert 'Существует более актуальная ссылка' in response.text


def get_payment_data(wrong_hash=False):
    """
    Параметры для post-запроса на уведомление
    """

    if wrong_hash:
        sha1_hash = 'c9d49da96164d1c2a458606e5047f72f3a5fbd5'
    else:
        sha1_hash = '849e3756087ee4de541e7bfdd0a0ddc118672b5e'

    data = {
        'notification_type': 'card-incoming',
        'bill_id': '',
        'amount': f'{77.60:.2f}',
        'codepro': 'false',
        'withdraw_amount': f'{80.00:.2f}',
        'unaccepted': 'false',
        'label': '3e2be2ac-8771-4923-bbad-125940a6d9df',
        'datetime': '2024-02-29T18:57:26Z',
        'sender': '',
        'sha1_hash': sha1_hash,
        'operation_label': '2d72e745-0011-5000-a000-1c531b25ba94&',
        'operation_id': '762548246564417096',
        'currency': '643'
    }

    return data


async def test_get_payment(ac: AsyncClient):
    """
    Тест уведомления: успешный
    """

    response = await ac.post(
        '/payment_notification',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=get_payment_data(),
    )

    print(response.text)

    assert response.status_code == 200


async def test_get_payment_hash_error(ac: AsyncClient):
    """
    Тест уведомления: неверная hash-сумма
    """

    response = await ac.post(
        '/payment_notification',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=get_payment_data(wrong_hash=True),
    )

    assert response.status_code == 400
    print(response)


async def test_get_payment_data_error(ac: AsyncClient):
    """
    Тест уведомления: запрос неправильно структурирован
    """

    response = await ac.post(
        '/payment_notification',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={},
    )

    print(response.status_code)

    assert response.status_code == 422