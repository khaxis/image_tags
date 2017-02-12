import luigi
import subprocess
import json
from tempfile import NamedTemporaryFile

class MakePool(luigi.Task):
    n_class = luigi.Parameter()
    image_tag_path = luigi.Parameter()

    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("target_new_pool_" + str(self.n_class))

    def run(self):
        f = NamedTemporaryFile()
        bashCommand = 'python -m learning_utils.make_pool --target %s --out %s' % (self.n_class, f.name)
        process = subprocess.Popen(['/bin/sh', '-c' , '-e', bashCommand], stdout=subprocess.PIPE, cwd=self.image_tag_path)
        output, error = process.communicate()
        if process.returncode == 0:
            with self.output().open('w') as out_file, open(f.name, 'r') as id_file:
                out_file.write(id_file.read())
        """
        print "-----------------"
        bashCommand = 'echo %s > %s' % ("helo world", self.output().path)

        process = subprocess.Popen(['/bin/sh', '-c' , '-e', bashCommand], stdout=subprocess.PIPE)
        output, error = process.communicate()
        print "-----------------"
        print output,'#', error, '$', process.returncode
        print "-----------------"
        """

class GetPoolStats(luigi.Task):
    n_class = luigi.Parameter()
    image_tag_path = luigi.Parameter()

    def requires(self):
        return MakePool(n_class=self.n_class, image_tag_path=self.image_tag_path)
 
    def output(self):
        return luigi.LocalTarget("target_pool_stats_" + str(self.n_class))

    def run(self):
        with self.input().open() as fin:
            pool_id = fin.read()

        f = NamedTemporaryFile()
        bashCommand = 'python -m learning_utils.get_pool_stats --pool %s --out %s' % (pool_id, f.name)
        process = subprocess.Popen(['/bin/sh', '-c' , '-e', bashCommand], stdout=subprocess.PIPE, cwd=self.image_tag_path)
        output, error = process.communicate()
        if process.returncode == 0:
            with self.output().open('w') as out_file, open(f.name, 'r') as id_file:
                out_file.write(id_file.read())


class GetSampledOrOriginalPool(luigi.Task):
    n_class = luigi.Parameter()
    image_tag_path = luigi.Parameter()
    sampled_pool_size = luigi.IntParameter(10000)

    def requires(self):
        return [
                    MakePool(n_class=self.n_class, image_tag_path=self.image_tag_path),
                    GetPoolStats(n_class=self.n_class, image_tag_path=self.image_tag_path)
               ]
 
    def output(self):
        return luigi.LocalTarget("target_get_sampled_pool_" + str(self.n_class) + "_" + str(self.sampled_pool_size))

    def run(self):
        with self.input()[0].open() as fin:
            pool_id = fin.read()
        with self.input()[1].open() as fin:
            pool_stats = json.loads(fin.read())

        sample_rate = float(self.sampled_pool_size) / pool_stats['pool_size']
        if sample_rate > 1.0:
            with self.output().open('w') as out_file, open(f.name, 'r') as id_file:
                out_file.write(pool_id)
        else:
            description = '%s - Sampled %d instances' % (pool_stats['description'], self.sampled_pool_size)
            f = NamedTemporaryFile()
            bashCommand = 'python -m learning_utils.sample_pool --pool %s --description "%s" --rate %f --out %s' % (pool_id, description, sample_rate, f.name)
            process = subprocess.Popen(['/bin/sh', '-c' , '-e', bashCommand], stdout=subprocess.PIPE, cwd=self.image_tag_path)
            output, error = process.communicate()
            if process.returncode == 0:
                with self.output().open('w') as out_file, open(f.name, 'r') as id_file:
                    out_file.write(id_file.read())


class FetchPool(luigi.Task):
    n_class = luigi.Parameter()
    image_tag_path = luigi.Parameter()
    sampled_pool_size = luigi.IntParameter(10000)

    def requires(self):
        return [GetSampledOrOriginalPool(n_class=self.n_class, image_tag_path=self.image_tag_path)]
 
    def output(self):
        return luigi.LocalTarget("target_fetched_pool_" + str(self.n_class))

    def run(self):
        with self.input()[0].open() as fin:
            pool_id = fin.read()
        
        bashCommand = 'python -m learning_utils.fetch_pool --pool %s' % (pool_id)
        process = subprocess.Popen(['/bin/sh', '-c' , '-e', bashCommand], stdout=subprocess.PIPE, cwd=self.image_tag_path)
        output, error = process.communicate()
        if process.returncode == 0:
            with self.output().open('w') as out_file:
                out_file.write(pool_id)


class TrainClassifier(luigi.Task):
    n_class = luigi.Parameter()
    image_tag_path = luigi.Parameter()
    sampled_pool_size = luigi.IntParameter(10000)

    def requires(self):
        return [FetchPool(n_class=self.n_class, image_tag_path=self.image_tag_path)]
 
    def output(self):
        return luigi.LocalTarget("target_train_classifier_pool_" + str(self.n_class))

    def run(self):
        with self.input()[0].open() as fin:
            pool_id = fin.read()

        f = NamedTemporaryFile()
        slices = 'bowSift100'
        name = '%s classifier' % self.n_class
        bashCommand = 'python -m learning_utils.train_classifier --pool-id %s --slices %s --name "%s" --nid %s --out %s' % (pool_id, slices, name, self.n_class, f.name)
        process = subprocess.Popen(['/bin/sh', '-c' , '-e', bashCommand], stdout=subprocess.PIPE, cwd=self.image_tag_path)
        output, error = process.communicate()
        if process.returncode == 0:
            with self.output().open('w') as out_file, open(f.name, 'r') as id_file:
                out_file.write(id_file.read())


if __name__ == "__main__":
    luigi.run()