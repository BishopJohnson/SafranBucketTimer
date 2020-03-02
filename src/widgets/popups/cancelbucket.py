# Custom packages
from src.widgets.popups.tributtonpopup import TriButtonPopup

from kivy.lang import Builder


Builder.load_file('src/kv/popups/cancelbucket.kv')


class CancelBucket(TriButtonPopup):
    def __init__(self, app, max_name_length=8, bucket_one_callback=None, bucket_two_callback=None, **kwargs):
        super(CancelBucket, self).__init__(mid_btn_callback=bucket_one_callback,
                                           right_btn_callback=bucket_two_callback,
                                           **kwargs)

        bucket_one = app.bucket_one.name
        bucket_two = app.bucket_two.name

        if len(bucket_one) > max_name_length:
            self.mid_btn_id.text = '{}...'.format(bucket_one[:max_name_length])
        else:
            self.mid_btn_id.text = '{}'.format(bucket_one)

        if len(bucket_two) > max_name_length:
            self.right_btn_id.text = '{}...'.format(bucket_two[:max_name_length])
        else:
            self.right_btn_id.text = '{}'.format(bucket_two)
