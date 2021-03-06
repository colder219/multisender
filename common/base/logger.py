# -*- coding: utf-8 -*-

"""
File Name：          logger
Description :
Author :             gregory
Date：               2018/3/30:上午10:54
Change Activity:     2018/3/30:上午10:54

"""

import sys
import types
import logging
import logging.config
from logging import DEBUG, INFO, WARN, ERROR, FATAL, NOTSET

LEVEL_COLOR = {
    DEBUG: '\33[2;39m',
    INFO: '\33[0;36m',
    WARN: '\33[0;33m',
    ERROR: '\33[0;35m',
    FATAL: '\33[1;31m',
    NOTSET: ''
}

log = None


class ScreenHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            fs = LEVEL_COLOR[record.levelno] + "%s\n" + '\33[0m'
            if not logging:
                stream.write(fs % msg)
            else:
                try:
                    if (isinstance(msg, str) and
                            getattr(stream, 'encoding', None)):
                        # ufs = fs.decode(stream.encoding)
                        ufs = fs
                        try:
                            stream.write(ufs % msg)
                        except UnicodeEncodeError:
                            stream.write((ufs % msg).encode(stream.encoding))
                    else:
                        stream.write(fs % msg)
                except UnicodeError:
                    stream.write(fs % msg.encode("UTF-8"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


logging.ScreenHandler = ScreenHandler


def debug(msg, *args, **kwargs):
    global log
    log.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    global log
    log.info(msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    global log
    log.warn(msg, *args, **kwargs)


warning = warn


def error(msg, *args, **kwargs):
    global log
    log.error(msg, *args, **kwargs)


def fatal(msg, *args, **kwargs):
    global log
    log.fatal(msg, *args, **kwargs)


critical = fatal


def install(logdict, **options):
    pyv = sys.version_info
    if pyv[0] == 2 and pyv[1] < 7:
        raise RuntimeError('python error, must python >= 2.7')

    if not isinstance(logdict, dict):
        logdict = {
            'root': {
                'filename': logdict,
            }
        }
        if options:
            logdict['root'].update(options)

    conf = {
        'version': 1,
        'formatters': {
            'myformat': {
                'format': '%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.ScreenHandler',
                'formatter': 'myformat',
                'level': 'DEBUG',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
        },
    }

    def get_log_conf(name, level='DEBUG'):
        filecf = {
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'myformat',
            'level': level.upper(),
            'filename': name,
        }
        if options:
            if 'when' in options:
                filecf.update({'class': 'logging.handlers.TimedRotatingFileHandler'})
            filecf.update(options)
        return filecf

    for logname, logcf in logdict.items():
        loggercf = None
        if logname == 'root':
            conf['root'] = {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
            loggercf = conf['root']
        else:
            loggercf = {}
            conf['loggers'][logname] = loggercf
        filename = logcf['filename']
        del logcf['filename']
        tfilename_str = type(filename) in (bytes, str)
        if tfilename_str and filename != 'stdout':
            conf['handlers']['file' + filename] = get_log_conf(filename)
            loggercf['handlers'] = ['file' + filename]
        elif not tfilename_str:
            filehandlers = []
            for level, name in filename.items():
                conf['handlers']['file-' + name] = get_log_conf(name, level)
                filehandlers.append('file-' + name)
            loggercf['handlers'] = filehandlers
    for logname in logdict:
        if logname != 'root':
            logobj = logging.getLogger(logname)
            logobj.propagate = False

    logging.config.dictConfig(conf)
    logobj = logging.getLogger()
    global log
    log = logobj
    return logobj


def test6():
    install({
        'root': {
            'filename': {'DEBUG': "test-info.log", 'ERROR': 'test-err.log'},
        },
        'mytest': {
            'filename': 'stdout',
        },
    })

    log1 = logging.getLogger()
    for i in range(0, 10):
        log1.debug('debug ... %d', i)
        log1.info('info ... %d', i)
        log1.warn('warn ... %d', i)
        log1.error('error ... %d', i)
        log1.fatal('fatal ... %d', i)

    log2 = logging.getLogger('mytest')
    for i in range(0, 10):
        log2.debug('debug ... %d', i)
        log2.info('info ... %d', i)
        log2.warn('warn ... %d', i)
        log2.error('error ... %d', i)
        log2.fatal('fatal ... %d', i)


def test1():
    install('stdout')
    log = logging.getLogger()
    for i in range(0, 1):
        log.debug('debug ... %d', i)
        log.info('info ... %d', i)
        log.warn('warn ... %d', i)
        log.error('error ... %d', i)
        log.fatal('fatal ... %d', i)


if __name__ == '__main__':
    test6()
    test1()
