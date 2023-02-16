import vk_api
from vk_config import *
from threading import Thread
from datetime import datetime
import datetime as dt
URS = "[+[X]-]"


TAF = {
    "users": {"id": int,
              "name": str,
              "email": str,
              "password": str,
              "time": str},
    "posts": {"post_id": int,
              "operation": str,
              "date": str,
              "car_id": int,
              "user_id": int,
              "note": str,
              "file_url": str,
              "file_name": str,
              "distance": int,
              "is_deleted": int},

    "cars": {"car_id": int,
             "user_id": int,
             "car_name": str,
             "description": str,
             "distance": int,
             "is_deleted": int,
             "number": str
             },
    "operations": {"operation": str,
                   "user_id": int,
                   "is_deleted": int,
                   "period": str}
}

"""    


tokens = get_tokens()

msg = download(token=get_tokens()['cars'])[0]
msg = {"peer_id": msg['peer_id'], "text": msg['text'], "id": msg['id']}
print(update(token=get_tokens()['cars'], msg_id=msg['id'], text='4',
             peer_id=msg['peer_id']))"""


def get_tokens() -> dict:
    import json
    with open('db/tables_tokens.json') as f:
        tokens = json.load(f)
    return tokens

def send(token: str, msg: str) -> tuple:
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        vk.messages.send(
            user_id=user_id,
            message=msg, random_id=0)
        return True, True
    except Exception as e:
        return False, str(e.args)

def download(token: str) -> list:
    vk_session = vk_api.VkApi(token=token)
    session_api = vk_session.get_api()
    lastMessage = session_api.messages.getHistory(count=1, peer_id=user_id)
    requestCount = int(lastMessage['items'][0]['id'] / 200 + 1)
    messages = []
    for i in range(1, requestCount + 1):
        history = session_api.messages.getHistory(count=200, peer_id=user_id,
                                                  start_message_id=200 * i)
        history = history['items']
        for j in reversed(history):
            if j['from_id'] != user_id:
                messages.append(j)
    return messages

def update(token: str, msg_id: int, text: str, peer_id: int) -> None:
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    (vk.messages.delete(delete_for_all=0, message_ids=msg_id))
    vk.messages.send(
        user_id=user_id,
        message=text, random_id=0)

class Local_API:
    def __init__(self):
        self.state = True
        self.db = Global_API()
        self.posts = []
        self.cars = []
        self.operations = []
        self.users = []
        self.update()

    def get_menu(self, is_logged, user_id) -> list:
        import json
        if not is_logged or not user_id:
            with open(
                    f'static/json/menu/menu_no_posts_no_archive.json',
                    encoding="utf-8") as file:
                data = json.load(file)
            return data

        no_archive = True
        no_posts = True
        posts_cars = set([post["car_id"] for post in self.get_posts(user_id)])
        cars = set([car["car_id"] for car in self.get_cars(user_id)])
        arx = set([arxc["car_id"] for arxc in self.get_archived_cars(user_id) if arxc["car_id"] != -1])


        if posts_cars - arx != posts_cars:
            no_archive = False
        if posts_cars - cars != posts_cars:
            no_posts = False

        with open(
                f'static/json/menu/{"menu" + "_logged" * is_logged + "_no_posts" * no_posts + "_no_archive" * no_archive + ".json"}',
                encoding="utf-8") as file:
            data = json.load(file)
        return data

    def update(self) -> None:
        self.state = False
        self.posts = self.db.get_objets("posts")
        self.cars = self.db.get_objets("cars")
        self.operations = self.db.get_objets("operations")
        self.users = self.db.get_objets("users")
        self.state = True

    def update_post(self, post_id, car_id, operation, distance, note) -> bool:
        post = {}
        for i in self.posts:
            if TAF["posts"]["post_id"](post_id) == TAF["posts"]["post_id"](
                    i["post_id"]) and TAF["posts"]["is_deleted"](
                    i["is_deleted"]) == 0:
                post = i
                break
        if post:
            post["car_id"] = TAF["posts"]["car_id"](car_id)
            post["operation"] = TAF["posts"]["operation"](operation)
            post["distance"] = TAF["posts"]["distance"](distance)
            post["note"] = TAF["posts"]["note"](note)
            for i in range(len(self.posts)):
                if TAF["posts"]["post_id"](post_id) == TAF["posts"]["post_id"](
                        self.posts[i]["post_id"]) and TAF["posts"][
                    "is_deleted"](
                    self.posts[i]["is_deleted"]) == 0:
                    self.posts[i] = post
                    break
            t1 = Thread(target=self.db.update_post,
                        args=(post_id, car_id, operation, distance, note), )
            t1.start()
        return bool(post)

    def update_car(self, car_id, car_name, distance, description, number) -> bool:
        car = {}
        for i in self.cars:
            if TAF["cars"]["car_id"](car_id) == TAF["cars"]["car_id"](
                    i["car_id"]) and TAF["cars"]["is_deleted"](
                i["is_deleted"]) == 0:
                car = i
                break
        if car:
            car["distance"] = TAF["cars"]["distance"](distance)
            car["description"] = TAF["cars"]["description"](description)
            car["number"] = TAF["cars"]["number"](number)
            car["car_name"] = TAF["cars"]["car_name"](car_name)
            for i in range(len(self.cars)):
                if TAF["cars"]["car_id"](car_id) == TAF["cars"]["car_id"](
                        self.cars[i]["car_id"]) and TAF["cars"]["is_deleted"](
                    self.cars[i]["is_deleted"]) == 0:
                    self.cars[i] = car
                    break
            t1 = Thread(target=self.db.update_car,
                        args=(car_id, car_name, distance, description, number))
            t1.start()
        return bool(car)

    def update_operation(self, user_id, old_value, new_value, period) -> bool:
        operation = {}
        old_value = old_value.strip()
        new_value = new_value.strip()
        for i in self.operations:
            if TAF["operations"]["user_id"](user_id) == TAF["operations"][
                "user_id"](
                    i["user_id"]) and TAF["operations"]["is_deleted"](
                i["is_deleted"]) == 0 and TAF["operations"]["operation"](
                old_value) == TAF["operations"]["operation"](
                i["operation"]):
                operation = i
                break
        if operation:
            operation["operation"] = TAF["operations"]["operation"](new_value)
            operation["period"] = TAF["operations"]["period"](period)

            for i in range(len(self.operations)):
                if TAF["operations"]["user_id"](user_id) == TAF["operations"][
                    "user_id"](
                    self.operations[i]["user_id"]) and TAF["operations"][
                    "is_deleted"](
                    self.operations[i]["is_deleted"]) == 0 and \
                        TAF["operations"]["operation"](
                            old_value) == TAF["operations"]["operation"](
                    self.operations[i]["operation"]):
                    self.operations[i] = operation
                    break
            t1 = Thread(target=self.db.update_operation,
                        args=(user_id, old_value, new_value, period))
            t1.start()
        return bool(operation)

    def delete_post(self, post_id) -> bool:
        post = {}
        for i in self.posts:
            if TAF["posts"]["post_id"](post_id) == TAF["posts"]["post_id"](
                    i["post_id"]) and TAF["posts"]["is_deleted"](
                i["is_deleted"]) == 0:
                post = i
                break
        if post:
            post["is_deleted"] = TAF["posts"]["is_deleted"](1)
            for i in range(len(self.posts)):
                if TAF["posts"]["post_id"](post_id) == TAF["posts"]["post_id"](
                        self.posts[i]["post_id"]) and TAF["posts"][
                    "is_deleted"](
                    self.posts[i]["is_deleted"]) == 0:
                    self.posts[i] = post
                    break
            t1 = Thread(target=self.db.delete_post,
                        args=(post_id, ))
            t1.start()
        return bool(post)

    def delete_car(self, car_id) -> bool:
        car = {}
        for i in self.cars:
            if TAF["cars"]["car_id"](car_id) == TAF["cars"]["car_id"](
                    i["car_id"]) and TAF["cars"]["is_deleted"](
                i["is_deleted"]) == 0:
                car = i
                break
        if car:
            car["is_deleted"] = TAF["cars"]["is_deleted"](1)
            for i in range(len(self.cars)):
                if TAF["cars"]["car_id"](car_id) == TAF["cars"]["car_id"](
                        self.cars[i]["car_id"]) and TAF["cars"]["is_deleted"](
                    self.cars[i]["is_deleted"]) == 0:
                    self.cars[i] = car
                    break
            t1 = Thread(target=self.db.delete_car,
                        args=(car_id, ))
            t1.start()
        return bool(car)

    def delete_operation(self, operation_v, user_id) -> bool:
        operation = self.get_operation(operation_v, user_id)
        for i in self.operations:
            if TAF["operations"]["user_id"](user_id) == TAF["operations"][
                "user_id"](
                i["user_id"]) and TAF["operations"]["is_deleted"](
                i["is_deleted"]) == 0 and TAF["operations"]["operation"](
                operation_v) == TAF["operations"]["operation"](
                i["operation"]):
                operation = i
                break
        if operation:
            operation["is_deleted"] = TAF["operations"]["operation"](1)
            for i in range(len(self.operations)):
                if TAF["operations"]["user_id"](user_id) == TAF["operations"][
                    "user_id"](
                    self.operations[i]["user_id"]) and TAF["operations"][
                    "is_deleted"](
                    self.operations[i]["is_deleted"]) == 0 and \
                        TAF["operations"]["operation"](
                            operation_v) == TAF["operations"]["operation"](
                    self.operations[i]["operation"]):
                    self.operations[i] = operation
                    break
            t1 = Thread(target=self.db.delete_operation,
                        args=(operation_v, user_id))
            t1.start()
        return bool(operation)

    def add_post(self, operation, car_id, user_id, distance, note, file_url,
                 file_name, update_distance) -> bool:

        offset = dt.timezone(dt.timedelta(hours=3))

        tm = f"{'0' * (2 - len(str(datetime.now(offset).day))) + str(datetime.now(offset).day)}.{'0' * (2 - len(str(datetime.now(offset).month))) + str(datetime.now(offset).month)}.{datetime.now(offset).year} {'0' * (2 - len(str(datetime.now(offset).hour))) + str(datetime.now(offset).hour)}:{'0' * (2 - len(str(datetime.now(offset).minute))) + str(datetime.now(offset).minute)}"

        new_post = {}
        next_id = max([int(i['post_id']) for i in self.posts] + [0]) + 1
        values = [next_id, operation, tm, car_id, user_id, note, file_url,
                  file_name, distance, 0]
        c = 0
        for key in TAF["posts"]:
            new_post[key] = TAF["posts"][key](values[c])
            c += 1
        if update_distance:
            car = self.get_car(car_id)
            self.update_car(car["car_id"], car["car_name"], distance, car["description"], car["number"])
        self.posts.append(new_post)
        t1 = Thread(target=self.db.add_post,
                    args=(operation, car_id, user_id, distance, note, file_url,
                          file_name))
        t1.start()
        return bool(new_post)

    def add_car(self, user_id, car_name, description, distance, number) -> bool:
        car_name = car_name.strip()
        description = description.strip()
        number = number.strip()
        next_id = max([int(i['car_id']) for i in self.cars] + [0]) + 1
        new_car = {}
        values = [next_id, user_id, car_name, description, distance, 0, number]
        c = 0
        for key in TAF["cars"]:
            new_car[key] = TAF["cars"][key](values[c])
            c += 1
        self.cars.append(new_car)
        t1 = Thread(target=self.db.add_car,
                    args=(user_id, car_name, description, distance, number))
        t1.start()
        return bool(new_car)

    def add_operation(self, operation, user_id, period) -> bool:
        if self.is_operation_exist(operation, user_id):
            return False
        operation = operation.strip()
        new_operation = {}
        values = [operation, user_id, 0, period]
        c = 0
        for key in TAF["operations"]:
            new_operation[key] = TAF["operations"][key](values[c])
            c += 1
        self.operations.append(new_operation)
        t1 = Thread(target=self.db.add_operation,
                    args=(operation, user_id, period))
        t1.start()
        return bool(new_operation)

    def add_user(self, username, email, hpsw) -> bool:
        if TAF["users"]["email"](email) in [
            TAF["users"]["email"](user["email"]) for user in self.users]:
            return False
        offset = dt.timezone(dt.timedelta(hours=3))

        tm = f"{'0' * (2 - len(str(datetime.now(offset).day))) + str(datetime.now(offset).day)}.{'0' * (2 - len(str(datetime.now(offset).month))) + str(datetime.now(offset).month)}.{datetime.now(offset).year} {'0' * (2 - len(str(datetime.now(offset).hour))) + str(datetime.now(offset).hour)}:{'0' * (2 - len(str(datetime.now(offset).minute))) + str(datetime.now(offset).minute)}"

        next_id = max([int(i['id']) for i in self.users] + [0]) + 1
        new_user = {}
        values = [next_id, username, email, hpsw, tm]
        c = 0
        for key in TAF["users"]:
            new_user[key] = TAF["users"][key](values[c])
            c += 1
        self.users.append(new_user)
        self.add_operation("не имеет значения", next_id, "")
        t1 = Thread(target=self.db.add_user,
                    args=(username, email, hpsw))
        t1.start()
        return bool(new_user)

    def get_posts(self, user_id) -> list:

        posts = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0), self.posts))
        return posts

    def get_cars(self, user_id) -> list:
        if not user_id:
            return []
        return list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0), self.cars))

    def get_operations(self, user_id) -> list:
        operations = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0), self.operations))
        return operations

    def get_operations_na(self, user_id) -> list:
        operations = list(list(filter(lambda x: (int(x['user_id']) == int(user_id)), self.operations)))
        r = []
        for i in operations:
            if i not in r:
                r.append(i)
        return r

    def is_operation_exist(self, operation, user_id) -> bool:
        return bool(self.get_operation(operation, user_id))

    def get_post(self, post_id) -> dict:
        for post in self.posts:
            if TAF["posts"]["post_id"](post["post_id"]) == int(post_id):
                return post
        return {}

    def get_car(self, car_id) -> dict:
        for car in self.cars:
            if int(car['car_id']) == int(car_id):
                if int(car['is_deleted']) == 0:
                    return car
        return {}


    def get_operation(self, operation_l, user_id) -> dict:
        operation_v= {}
        for operation in self.operations:

            if TAF['operations']['user_id'](operation['user_id']) == TAF['operations']['user_id'](user_id):
                if TAF['operations']['is_deleted'](operation['is_deleted']) == 0:
                    if TAF['operations']['operation'](operation['operation']) == TAF['operations']['operation'](operation_l):
                        operation_v = operation
                        break
        return operation_v

    def get_user(self, user_id) -> list:
        user = list(filter(
            lambda x: ((int(x['id'])) == int(user_id)), self.users))

        return user

    def get_archived_cars(self, user_id) -> list:
        if not user_id:
            return []
        return list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 1), self.cars))

    def get_archived_car(self, car_id) -> dict:
        for car in self.cars:
            if car["is_deleted"] == 1:
                if car["car_id"] == car_id:
                    return car
        return {}

    def get_user_by_username(self, email) -> list:
        user = list(filter(
            lambda x: ((x['email']) == email), self.users))
        return user

    def get_car_id(self, car_name, user_id) -> int:
        for car in self.cars:
            if car["car_name"] == car_name:
                if int(car["is_deleted"]) == 0:
                    if int(car["user_id"]) == int(user_id):
                        return int(car["car_id"])
        return -1

    def is_post_deleted(self, post) -> bool:
        post_id = TAF["posts"]["post_id"](post["post_id"])
        post = list(filter(
            lambda x: int(x['post_id']) == int(post_id), self.posts))[0]
        if post:
            return int(post['is_deleted']) == 1
        return True # если пост не найден - равнослильно тому, что он удален

    def is_car_deleted(self, car_id) -> bool:
        for car in self.cars:
            if int(car["car_id"]) == int(car_id):
                #print(car_id)
                return int(car["is_deleted"]) == 1
        return True





class Global_API:
    def __init__(self):
        self.state = True
        self.posts = self.get_objets("posts")
        self.cars = self.get_objets("cars")
        self.operations = self.get_objets("operations")
        self.users = self.get_objets("users")

    def update_post(self, post_id, car_id, operation, distance, note):
        posts = self.get_objets('posts')
        post = list(filter(
            lambda x: (int(x['post_id']) == int(post_id)) and (
                    int(x['is_deleted']) == 0), posts))[0]
        msg = self.get_msg_info('posts', post)
        update(token=get_tokens()['posts'], text=URS.join([str(i) for i in
                                                           [post['post_id'],
                                                            operation,
                                                            post['date'],
                                                            car_id,
                                                            post['user_id'],
                                                            note,
                                                            post['file_url'],
                                                            post['file_name'],
                                                            distance,
                                                            0]]),
               peer_id=msg['peer_id'],
               msg_id=msg['id'])
        return True

    def update_car(self, car_id, car_name, distance, description, number):
        cars = self.get_objets('cars')
        car = list(filter(
            lambda x: (int(x['car_id']) == int(car_id)) and (
                    int(x['is_deleted']) == 0), cars))[0]
        msg = self.get_msg_info('cars', car)
        update(token=get_tokens()['cars'], text=URS.join([str(i) for i in
                                                          [car['car_id'],
                                                           car['user_id'],
                                                           car_name,
                                                           description,
                                                           distance, 0,
                                                           number]]),
               peer_id=msg['peer_id'],
               msg_id=msg['id'])
        return True

    def update_operation(self, user_id, old_value, new_value, period):

        operations = self.get_objets('operations')
        operation = list(filter(
            lambda x: ((x['operation']) == old_value) and (
                    int(x['is_deleted']) == 0) and (
                              int(x['user_id']) == int(user_id)),
            operations))[0]
        msg = self.get_msg_info('operations', operation)
        update(token=get_tokens()['operations'], text=URS.join([str(i) for i in
                                                                [new_value,
                                                                 operation[
                                                                     'user_id'],
                                                                 0, period
                                                                 ]]),
               peer_id=msg['peer_id'],
               msg_id=msg['id'])
        return True

    def get_menu(self, is_logged, user_id):
        import json
        if not is_logged or not user_id:
            with open(
                    f'static/json/menu/menu_no_posts_no_archive.json',
                    encoding="utf-8") as file:
                data = json.load(file)
            return True, data

        no_archive = True
        no_posts = True
        posts_cars = set([self.make_diction("posts", i)['car_id'] for i in
                          (self.get_posts_titles(user_id))[1]])

        cars = set([self.make_diction("cars", i)['car_id'] for i in
                    self.get_cars(user_id)[1]])
        arx = set([self.make_diction("cars", i)['car_id'] for i in
                   self.get_archived_cars(user_id)[1]])
        if posts_cars - arx != posts_cars:
            no_archive = False
        if posts_cars - cars != posts_cars:
            no_posts = False
        with open(
                f'static/json/menu/{"menu" + "_logged" * is_logged + "_no_posts" * no_posts + "_no_archive" * no_archive + ".json"}',
                encoding="utf-8") as file:
            data = json.load(file)
        return True, data

    def get_user_fields(self, is_logged):
        import json
        with open(
                f'db/json/menu/{"menu" + "_logged" * is_logged + ".json"}',
                encoding="utf-8") as file:
            data = json.load(file)
        return True, data

    def get_operations(self, user_id):
        operations = self.get_objets('operations')
        operations = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0), operations))
        return True, operations

    def is_operation_exist(self, operation, user_id):
        return bool(self.get_operation(operation, user_id)[1])

    def get_operation(self, operation, user_id):
        operations = self.get_objets('operations')
        operation = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0) and (
                              x['operation'] == operation), operations))
        return True, operation

    def delete_operation(self, operation, user_id):

        operations = self.get_objets('operations')
        operation = list(filter(
            lambda x: ((x['operation']) == operation) and (
                    int(x['is_deleted']) == 0) and (
                              int(x['user_id']) == int(user_id)),
            operations))[0]
        msg = self.get_msg_info('operations', operation)
        update(token=get_tokens()['operations'], text=URS.join([str(i) for i in
                                                                [operation[
                                                                     'operation'],
                                                                 operation[
                                                                     'user_id'],
                                                                 1, ""
                                                                 ]]),
               peer_id=msg['peer_id'],
               msg_id=msg['id'])
        return True



    def add_operation(self, operation, user_id, period):
        if self.is_operation_exist(operation, user_id):
            return False, 'такой тип работ уже есть'
        send(token=get_tokens()['operations'], msg=URS.join([str(i) for i in
                                                             [operation,
                                                              user_id,
                                                              0,
                                                              period]]))
        return [True]

    def add_post(self, operation, car_id, user_id, distance, note, file_url,
                 file_name):
        offset = dt.timezone(dt.timedelta(hours=3))

        tm = f"{'0' * (2 - len(str(datetime.now(offset).day))) + str(datetime.now(offset).day)}.{'0' * (2 - len(str(datetime.now(offset).month))) + str(datetime.now(offset).month)}.{datetime.now(offset).year} {'0' * (2 - len(str(datetime.now(offset).hour))) + str(datetime.now(offset).hour)}:{'0' * (2 - len(str(datetime.now(offset).minute))) + str(datetime.now(offset).minute)}"

        posts = self.get_objets('posts')
        next_id = max([int(i['post_id']) for i in posts] + [0]) + 1

        send(token=get_tokens()['posts'], msg=URS.join([str(i) for i in
                                                        [next_id, operation,
                                                         tm,
                                                         car_id, user_id,
                                                         note, file_url,
                                                         file_name, distance,
                                                         0]]))
        return [True]

    def is_post_deleted(self, post):
        post_id = int(self.make_diction("posts", post)['post_id'])
        posts = self.get_objets('posts')
        post = list(filter(
            lambda x: int(x['post_id']) == int(post_id), posts))[0]
        return True, int(post['is_deleted']) == 1

    def get_posts_titles(self, user_id):

        posts = self.get_objets('posts')
        posts = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0), posts))
        return True, posts

    def add_user(self, username, email, hpsw):
        offset = dt.timezone(dt.timedelta(hours=3))

        tm = f"{'0' * (2 - len(str(datetime.now(offset).day))) + str(datetime.now(offset).day)}.{'0' * (2 - len(str(datetime.now(offset).month))) + str(datetime.now(offset).month)}.{datetime.now(offset).year} {'0' * (2 - len(str(datetime.now(offset).hour))) + str(datetime.now(offset).hour)}:{'0' * (2 - len(str(datetime.now(offset).minute))) + str(datetime.now(offset).minute)}"

        users = self.get_objets('users')
        next_id = max([int(i['id']) for i in users] + [0]) + 1
        if email in [i['email'] for i in users]:
            return False, 'Пользователь существует'
        send(token=get_tokens()['users'], msg=URS.join([str(i) for i in
                                                        [next_id, username,
                                                         email, hpsw, tm]]))
        send(token=get_tokens()['operations'],
             msg=URS.join([str(i) for i in ['не имеет значения', next_id, 0, ""]]))
        return [True]

    def getUser(self, user_id):

        users = self.get_objets('users')
        user = list(filter(
            lambda x: ((int(x['id'])) == int(user_id)), users))
        if not user:
            return False, 'Пользователь не найден'
        return True, user[0]

    def get_user_by_username(self, email):

        users = self.get_objets('users')
        user = list(filter(
            lambda x: ((x['email']) == email), users))[0]
        return True, user

    def delete_posts(self):
        sql = "DROP TABLE IF EXISTS posts"
        r = self.execute_script(1, sql)
        if not r[0]:
            return 'E: ' + r[1]
        return 'done'

    def delete_post(self, post_id):

        posts = self.get_objets('posts')
        post = list(filter(
            lambda x: (int(x['post_id']) == int(post_id)) and (
                    int(x['is_deleted']) == 0), posts))[0]
        msg = self.get_msg_info('posts', post)
        update(token=get_tokens()['posts'], text=URS.join([str(i) for i in
                                                           [post['post_id'],
                                                            post['operation'],
                                                            post['date'],
                                                            post['car_id'],
                                                            post['user_id'],
                                                            post['note'],
                                                            post['file_url'],
                                                            post['file_name'],
                                                            post['distance'],
                                                            1]]),
               peer_id=msg['peer_id'],
               msg_id=msg['id'])
        return True

    def add_car(self, user_id, car_name, description, distance, number):
        cars = self.get_objets('cars')
        next_id = max([int(i['car_id']) for i in cars] + [0]) + 1
        send(token=get_tokens()['cars'], msg=URS.join([str(i) for i in
                                                       [next_id, user_id,
                                                        car_name, description,
                                                        distance, 0, number]]))
        return [True]

    def is_car_deleted(self, car_id):
        cars = self.get_objets('cars')
        car = list(filter(
            lambda x: int(x['car_id']) == int(car_id), cars))[0]
        return True, int(car['is_deleted']) == 1

    def get_post(self, post_id):
        posts = self.get_objets('posts')
        post = list(filter(
            lambda x: (int(x['post_id']) == int(post_id)) and (
                    int(x['is_deleted']) == 0), posts))[0]
        return True, post

    def get_archived_car(self, car_id):
        cars = self.get_objets('cars')
        car = list(filter(
            lambda x: (int(x['car_id']) == int(car_id)) and (
                    int(x['is_deleted']) == 1), cars))[0]
        return True, car

    def get_car(self, car_id):

        cars = self.get_objets('cars')
        car = list(filter(
            lambda x: (int(x['car_id']) == int(car_id)) and (
                    int(x['is_deleted']) == 0), cars))[0]
        return True, car

    def delete_car(self, car_id):
        cars = self.get_objets('cars')
        car = list(filter(
            lambda x: (int(x['car_id']) == int(car_id)) and (
                    int(x['is_deleted']) == 0), cars))[0]
        msg = self.get_msg_info('cars', car)
        update(token=get_tokens()['cars'], text=URS.join([str(i) for i in
                                                          [car['car_id'],
                                                           car['user_id'],
                                                           car['car_name'],
                                                           car['description'],
                                                           car['distance'], 1,
                                                           car['number']]]),
               peer_id=msg['peer_id'],
               msg_id=msg['id'])
        return True

    def get_archived_cars(self, user_id):
        cars = self.get_objets('cars')
        cars = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 1), cars))
        return True, cars

    def get_cars(self, user_id):
        if not user_id:
            return False,
        cars = self.get_objets('cars')

        cars = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0), cars))
        return True, cars

    def get_car_id(self, car_name, user_id):
        cars = self.get_objets('cars')
        cars = list(filter(
            lambda x: (int(x['user_id']) == int(user_id)) and (
                    int(x['is_deleted']) == 0) and (x['car_name'] == car_name),
            cars))
        return True, [cars]

    def make_diction(self, table_name: str, element) -> dict:
        if isinstance(element, dict):
            return element
        diction = {}
        key_words = [key for key in TAF[table_name]]

        for field_num in range(len(key_words)):
            diction[key_words[field_num]] = TAF[table_name][key_words[field_num]](element[field_num])
        return diction

    def get_objets(self, obj_type) -> list:
        messages = download(token=get_tokens()[obj_type])
        objects = [self.make_diction(obj_type, i['text'].split(URS)) for i in
                   messages]
        return objects

    def get_msg_info(self, table_name, text):
        text = URS.join([str(text[i]) for i in text])
        msgs = download(token=get_tokens()[table_name])
        msg = list(filter(lambda x: x['text'] == text, msgs))[0]
        msg = {"peer_id": msg['peer_id'], "text": msg['text'], "id": msg['id']}
        return msg


if __name__ == '__main__':
    print(input().split(URS))
