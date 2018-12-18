from flask import Flask, request, Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, PictureMessage, SuggestedResponseKeyboard, TextResponse, StartChattingMessage
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='db_kik')
curs = conn.cursor()

class KikBot(Flask):

    """ Flask kik bot application class"""

    def __init__(self, kik_api, import_name, static_path=None, static_url_path=None, static_folder="static",
                 template_folder="templates", instance_path=None, instance_relative_config=False,
                 root_path=None):

        self.kik_api = kik_api

        super(KikBot, self).__init__(import_name, static_path, static_url_path, static_folder, template_folder,
                                     instance_path, instance_relative_config, root_path)

        self.route("/incoming", methods=["POST"])(self.incoming)

    def incoming(self):
        """Handle incoming messages to the bot. All requests are authenticated using the signature in
        the 'X-Kik-Signature' header, which is built using the bot's api key (set in main() below).
        :return: Response
        """
        # verify that this is a valid request
        if not self.kik_api.verify_signature(
                request.headers.get("X-Kik-Signature"), request.get_data()):
            return Response(status=403)

        messages = messages_from_json(request.json["messages"])

        response_messages = []

        for message in messages:
            user = self.kik_api.get_user(message.from_user)
            # Check if its the user's first message. Start Chatting messages are sent only once.
            if isinstance(message, StartChattingMessage):

                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="haloo {}, pilihlah salah satu?".format(user.first_name),
                    # keyboards are a great way to provide a menu of options for a user to respond with!
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("Good"), TextResponse("ga")])]))


            # Check if the user has sent a text message.
            elif isinstance(message, TextMessage):
                user = self.kik_api.get_user(message.from_user)
                message_body = message.body.lower()
                print(message_body)
                sql = """insert into tb_inbox(user, message)
                        values ('%s','%s')""" % (user.first_name, message_body)
                print("Berhasil Menginputkan")

                curs.execute(sql)

                conn.commit()

                if message_body.split()[0] in ["hi", "hello", "hallo"]:
                    query = "SELECT in_message FROM tb_perintah"
                    curs.execute(query)
                    menu = curs.fetchall()
                    print(message_body)
                    print(menu)
                    msg = "List Menu !!\n"
                    iterasi = 1
                    for x in menu:
                        for y in x:
                            print(y)
                            msg = msg + ""+str(iterasi)+". "+y+"\n"
                        iterasi+=1
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body=msg.format(user.first_name),
                        keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("1"), TextResponse("2"), TextResponse("3"), TextResponse("4")])]))

                    query = "INSERT INTO tb_outbox (user,message,status) VALUES('%s','%s','1')" % (user.first_name, message_body)
                    curs.execute(query)
                    conn.commit()


                elif message_body.startswith("#"):

                    msg = message_body.split()

                    print(msg[0])

                    query = "SELECT query FROM tb_perintah WHERE marker = '%s' " % (msg[0])

                    print(query)

                    try:

                        curs.execute(query)

                    except:

                        print("ERROR")

                    menu = curs.fetchone()

                    print(menu[0])

                    if menu != None:

                        try:

                            msgProdi = msg[6] + " " + msg[7]

                            print(msgProdi)

                            qry = menu[0] % ("%" + msg[3] + "%", "%" + msgProdi + "%")

                        except:

                            print("INDEX MESSAGE TIDAK DITEMUKAN")

                            qry = menu[0]

                        print(qry)

                        curs.execute(qry)

                        data = curs.fetchall()

                        iterasi = 0

                        teks = ""

                        msgNew = ""

                        for row in data:

                            for i in curs.description:
                                print(i[0])

                                print(row[iterasi])

                                msgNew = msgNew + (i[0] + " = " + str(row[iterasi]) + "\n")

                                iterasi += 1

                                # if iterasi == i*4:

                                #     msgNew = "\n"

                                # else:

                                #     msgNew = ""

                            iterasi = 0

                    query = "INSERT INTO tb_outbox (user,message,status) VALUES('%s','%s','0')" % (

                        user.first_name, message_body)

                    print(query)

                    curs.execute(query)

                    conn.commit()

                    response_messages.append(TextMessage(

                        to=message.from_user,

                        chat_id=message.chat_id,

                        body=msgNew))

                else:
                    print(int(message_body))
                    query = "SELECT * FROM tb_perintah WHERE id_perintah = %i " %(int(message_body))
                    curs.execute(query)
                    menu = curs.fetchone()
                    print(message.from_user)
                    print(message.chat_id)
                    print(menu[2])
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body=menu[2].format(user.first_name)))

                query = "INSERT INTO tb_outbox (user,message,status) VALUES('%s','%s','1')" % (user.first_name, message_body, )
                curs.execute(query)
                conn.commit()

                #query = "INSERT INTO tb_outbox (user,message) VALUES('%s','%s')" % (user.first_name, message_body)
                #curs.execute(query)
                #conn.commit()

                # elif message_body == "1":
                #     response_messages.append(TextMessage(
                #         to=message.from_user,
                #         chat_id=message.chat_id,
                #         body="masukan nama mahasiswa :",
                #         keyboards=[SuggestedResponseKeyboard(
                #             responses=[TextResponse("miftah")])]))
                #
                #
                #
                # elif message_body == "2":
                #     response_messages.append(TextMessage(
                #         to=message.from_user,
                #         chat_id=message.chat_id,
                #         body="Masukan nama dosen :",
                #         keyboards=[SuggestedResponseKeyboard(
                #             responses=[TextResponse("boleh"), TextResponse("tidak")])]))
                #
                # elif message_body == "3":
                #     response_messages.append(TextMessage(
                #         to=message.from_user,
                #         chat_id=message.chat_id,
                #         body="masukan semua mahasiswa :",
                #         keyboards=[SuggestedResponseKeyboard(
                #             responses=[TextResponse("boleh"), TextResponse("tidak")])]))
                #
                # elif message_body == "4":
                #     response_messages.append(TextMessage(
                #         to=message.from_user,
                #         chat_id=message.chat_id,
                #         body="masukan semua dosen :",
                #         keyboards=[SuggestedResponseKeyboard(
                #             responses=[TextResponse("boleh"), TextResponse("tidak")])]))
                #


                    # Send the user a response along with their profile picture (function definition is below)




            #
            #     elif message_body in ["Engga","tidak", "Gak mau"]:
            #         response_messages.append(TextMessage(
            #             to=message.from_user,
            #             chat_id=message.chat_id,
            #             body="Okedeh, {}. Semangat yaa, jangan lupa chat aku lagi :)".format(user.first_name)))
            #     else:
            #         response_messages.append(TextMessage(
            #             to=message.from_user,
            #             chat_id=message.chat_id,
            #             body="maaf om {}, saya ga ngerti yang di maksud".format(user.first_name),
            #             keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("boleh"), TextResponse("Engga")])]))

            # If its not a text message, give them another chance to use the suggested responses
            else:

                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="maaf itu apa ya {}?".format(user.first_name),
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("Good"), TextResponse("Bad")])]))

            # We're sending a batch of messages. We can send up to 25 messages at a time (with a limit of
            # 5 messages per user).

            self.kik_api.send_messages(response_messages)

        return Response(status=200)




    @staticmethod
    def profile_pic_check_messages(user, message):
        """Function to check if user has a profile picture and returns appropriate messages.
        :param user: Kik User Object (used to acquire the URL the profile picture)
        :param message: Kik message received by the bot
        :return: Message
        """

        messages_to_send = []
        profile_picture = user.profile_pic_url

        if profile_picture is not None:
            messages_to_send.append(
                # Another type of message is the PictureMessage - your bot can send a pic to the user!
                PictureMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    pic_url=profile_picture
                ))

            profile_picture_response = "ini dia foto kamuu!"
        else:
            profile_picture_response = "ga mirip loh, yaudh lah yaa"

        messages_to_send.append(
            TextMessage(to=message.from_user, chat_id=message.chat_id, body=profile_picture_response))

        return messages_to_send


if __name__ == "__main__":
    """ Main program """
    kik = KikApi('botmca', 'fffa79e9-afe9-45e4-b2bd-6ec78732b3de')
    # For simplicity, we're going to set_configuration on startup. However, this really only needs to happen once
    # or if the configuration changes. In a production setting, you would only issue this call if you need to change
    # the configuration, and not every time the bot starts.
    kik.set_configuration(Configuration(webhook='https://c6aaa154.ngrok.io/incoming'))
    app = KikBot(kik, __name__)
    app.run(port=8080, host='127.0.0.1', debug=True)
