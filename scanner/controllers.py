from .workers import worker_func
from .utils import slice_list, slice_range, update_stats
import threading
import multiprocessing
import time

class Controller:
    def __init__(self, arguments):
        self.arguments = arguments
        self.count_queue = multiprocessing.Queue()
        self.workers = []
        self.proxies = []

        self.load_proxies()
        self.start_workers()
        self.start_stat_thread()

    def load_proxies(self):
        if not self.arguments.proxy_file:
            return
        with self.arguments.proxy_file:
            while True:
                line = self.arguments.proxy_file.readline()
                if not line:
                    break
                host, _, port = line.partition(":")
                self.proxies.append((host, int(port)))

    def start_stat_thread(self):
        def stat_updater_func():
            count_cache = []
            while any(w.is_alive() for w in self.workers):
                count_cache.append(self.count_queue.get())
                t = time.time()
                count_cache = [x for x in count_cache if 60 > t - x[0]]
                cpm = sum([x[1] for x in count_cache])
                update_stats(f"CPM: {cpm}")
        thread = threading.Thread(target=stat_updater_func)
        thread.start()
            
    def start_workers(self):
        barrier = multiprocessing.Barrier(self.arguments.workers + 1)
        for num in range(self.arguments.workers):
            worker = multiprocessing.Process(
                target=worker_func,
                kwargs=dict(
                    worker_num=num,
                    worker_barrier=barrier,
                    thread_count=self.arguments.threads,
                    count_queue=self.count_queue,
                    proxy_list=slice_list(self.proxies, num, self.arguments.workers),
                    gid_range=slice_range(self.arguments.range, num, self.arguments.workers),
                    gid_cutoff=self.arguments.cut_off,
                    gid_chunk_size=self.arguments.chunk_size,
                    webhook_url=self.arguments.webhook_url,
                    response_timeout=self.arguments.timeout
                )
            )
            self.workers.append(worker)
        for worker in self.workers:
            worker.start()
        barrier.wait()