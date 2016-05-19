from setuptools import setup,find_packages
import os
import setuptools.command.sdist

class SdistCommand(setuptools.command.sdist.sdist):
    def run(self):
        try:
            import pypandoc

            rst = pypandoc.convert("README.md", "rst")
            with open("README.txt", "w") as f:
                f.write(rst)
            print("convert markdown to rst")
        except Exception as e:
            raise e


        super(SdistCommand, self).run()
        os.remove("README.txt")


setup(
    cmdclass={'sdist': SdistCommand},
    name='elitech-datareader',
    version='0.9.4',
    packages=find_packages(),
    url='http://github.com/civic/elitech-datareader/',
    license='MIT',
    author='civic',
    author_email='dev@civic-apps.com',
    description='Elitech rc4 data access tool and library.',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms='any',
    test_suite = "tests",
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points="""
    [console_scripts]
    elitech-datareader=scripts.elitech_device:main
    """,
    dependency_links=["http://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx"]

)
