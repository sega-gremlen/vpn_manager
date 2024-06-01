import requests
from settings import MY_HOSTING

# get_payment(
#         notification_type: Annotated[str, Form()],
#         operation_id: Annotated[str, Form()],
#         amount: Annotated[str, Form()],
#         currency: Annotated[str, Form()],
#         datetime: Annotated[dt, Form()],
#         sender: Annotated[str, Form()],
#         codepro: Annotated[str, Form()],
#         test_notification: Annotated[str, Form()],
#         sha1_hash: Annotated[str, Form()],
#         label: Annotated[str, Form()] = '',
#         unaccepted: Annotated[str, Form()] = '',
#         withdraw_amount: Annotated[str, Form()] = '',
# ):

# data = ('notification_type=asdas&'
#         'operation_id=sdfsdf&'
#         'amount=nbnm&'
#         'currency=bnmbnm&'
#         'datetime=2024-02-28T21:02:49Z&'
#         'sender=test&'
#         'codepro=asdsad&'
#         'test_notification=bnmbnm&'
#         'sha1_hash=1sdasd&'
#         'label=asdsssssss&'
#         'unaccepted=123asd&'
#         'withdraw_amount=123'
#         )

data = ('notification_type=card-incoming&'
        'bill_id=&'
        'amount=48.5&'
        'codepro=false&'
        'withdraw_amount=50.00&'
        'unaccepted=false&'
        'label=e5819011-01d5-4431-a352-a567ce6fccbe&'
        'datetime=2024-02-29T18%3A57%3A26Z&sender=&'
        'sha1_hash=4d8c9abbe818ec9f158f0e215f703c480a46a695&'
        'operation_label=2d72e745-0011-5000-a000-1c531b25ba94&'
        'operation_id=762548246564417096&'
        'currency=643')

# print(data)


response = requests.post(f'{MY_HOSTING}/payment_notification',
                         headers={'Content-Type': 'application/x-www-form-urlencoded'},
                         data=data)

print(response)

# https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=50&label=MM
