url = 'https://yoomoney.ru/quickpay/confirm'
receiver = 4100118561425598
quickpay_form = 'button'
payment_type = 'AC'
sum_ = 300
label = 'subscription_id'

final_url = f'{url}/?receiver={receiver}&quickpay-form={quickpay_form}&paymentType={payment_type}&sum={sum_}'
print(final_url)