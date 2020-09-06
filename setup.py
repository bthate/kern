from setuptools import setup

def readme():
    with open('README') as file:
        return file.read()

setup(
    name='kern',
    version='20',
    url='https://bitbucket.org/bthate/kern',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="kern provides a object as json files backend, event handler and console code.",
    long_description=readme(),
    license='Public Domain',
    packages=["kern"],
    namespace_packages=["kern"],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: Public Domain',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Topic :: Utilities'
                ]
)
