import multiprocessing as mp
from . import sc_api_calls as scac


class Consumer(mp.Process):
    def __init__(self, task_queue, result_queue):
        mp.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            next_task = self.task_queue.get()
            # Poison pill means we should exit
            if next_task is None:
                break
            answers = next_task()
            # dequeue one at a time
            for answer in answers:
                self.result_queue.put([next_task.artist, next_task.action, answer])
            # poison pill to indiciate we finished this task
            self.result_queue.put([next_task.artist, next_task.action, None])
        return


class Task(object):
    def __init__(self, artist, action):
        self.artist = artist
        self.action = action

    def __call__(self):
        actions = {
            "followings": scac.getFollowings,
            "followers": scac.getFollowers,
            "favorites": scac.getFavorites,
            "comments": scac.getComments,
            "tracks": scac.getTracks,
        }
        # initialResults = actions[self.action](self.artist)
        initialResults = None
        return actions[self.action](scac.getUserid(self.artist))
        results = []
        for artist in initialResults:
            userid = None
            if hasattr(artist, "id"):
                userid = artist.id
            elif hasattr(artist, "user"):
                userid = artist.user["id"]
            else:
                print("\t", artist)
            results.append(userid)
        results = list(set(results))
        results = [result for result in results if result]
        return results

    def __str__(self):
        return "Get %s: %s" % (self.action, self.artist)


def bookTasks(tasksQueue, artist):
    actions = ["followings", "followers", "favorites", "comments", "tracks"]
    for action in actions:
        print("Booking tasks ", action)
        tasksQueue.put(Task(artist, action))
    # number of tasks we've added
    return len(actions)
