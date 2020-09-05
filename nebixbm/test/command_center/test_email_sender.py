# import unittest
# import os
#
# from nebixbm.command_center.notification.email import EmailSender
#
#
# def delete_file(filename):
#     """Deletes given file"""
#     if os.path.isfile(filename):
#         os.remove(filename)
#         return True
#     else:
#         return False
#
#
# class TestValidator(unittest.TestCase):
#     """Tests for EmailSender"""
#
#     def setUp(self):
#         """Sets up for each test"""
#         self.email_sender = EmailSender(
#             sender_email="",  # TODO
#             password="",  # TODO
#             smtp_host="smtp.gmail.com",
#         )
#         self.file = "test.csv"
#         with open(self.file, "w+"):
#             pass
#
#     def test_send_email(self):
#         """Test to send an email"""
#         msg = (
#             "Hi,\n\nThis is a notification "
#             "from Nebix Team.\n\nHave a good day!"
#         )
#         resp = self.email_sender.send_email(
#             "",  # TODO
#             "Test Email!",
#             msg,
#             html=None,
#             filenames=[self.file],
#         )
#
#         self.assertTrue(resp)
#
#     def tearDown(self):
#         """Sets up for each test"""
#         self.assertTrue(delete_file(self.file))
