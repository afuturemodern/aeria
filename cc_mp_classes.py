import multiprocessing as mp
import sc_api_calls as scac

class Consumer(mp.Process):
    def __init__(self, task_queue, result_queue):
        mp.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                                # print "%s is dying!" % proc_name
                # Poison pill means we should exit
                break
            answer = next_task()
            self.result_queue.put([next_task.artist, next_task.action, answer])
        return

class Task(object):
    def __init__(self, artist, action):
        self.artist = artist
        self.action = action
    def __call__(self):
        actions = {"followings": scac.getFollowings,
                    "followers": scac.getFollowers,
                    "favorites": scac.getFavorites,
                    "comments": scac.getComments,
                    "tracks": scac.getTracks}
        initialResults = actions[self.action](self.artist)
        results = list(set([artist for artist in initialResults if scac.id2username(artist)]))
        return results
    def __str__(self):
        return 'Get %s: %s' % (self.action, self.artist)

def bookTasks(tasksQueue, artist):
    actions = ["followings",
                "followers",
                "favorites",
                "comments",
                "tracks"]
    for action in actions:
        tasksQueue.put(Task(artist, action))
