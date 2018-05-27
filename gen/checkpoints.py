import os
import glob
import pickle
import datetime

class CheckpointManager:
    def __init__(self, checkpoint_dir):
        if checkpoint_dir is None:
            checkpoint_dir = os.path.join('checkpoints', str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')))

        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        self.checkpoint_dir = checkpoint_dir
        self.last_epoch = int(os.path.basename(max(glob.glob(os.path.join(checkpoint_dir, '*.pkl')),
                                                   default='-1.pkl'))[:-4])

    def checkpoint_path(self, epoch):
        return os.path.join(self.checkpoint_dir, '%d.pkl' % epoch)

    def save(self, population, seed):
        self.last_epoch += 1

        with open(self.checkpoint_path(self.last_epoch), 'wb') as f:
            pickle.dump([population, seed], f)

    def save_decorator(self, foo):
        def wrapper(population, seed, *args, **kwargs):
            self.save(population, seed)

            return foo(population, seed, *args, **kwargs)

        return wrapper

    def load_epoch(self, epoch):
        with open(self.checkpoint_path(epoch), 'rb') as f:
            return pickle.load(f)
