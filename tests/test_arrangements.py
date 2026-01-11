from twisted.internet import defer, reactor

from cccp.async.head import HeadClient
from cccp.async.dispatch import DispatchClient
from cccp.async.ccxml import CcxmlClient

from ivcommons.log import Log

log = Log("Test Librairie")

def do_init():
    test2()

@defer.inlineCallbacks
def test1():
    head = HeadClient("svc-ics-int-cst-fr-301.hostics.fr", 20000)
    yield head.connect()

    result = yield head.list("/proc/localhost")
    log.debug("head.list(): %s" % result)
    resultdispatch = yield head.get("/proc/"+result[0]+"/Head_INT101/Dispatch")
    log.debug("head.get(): (port) %s" % resultdispatch.port)

    dispatch = DispatchClient("svc-ics-int-cst-fr-301.hostics.fr", resultdispatch.port)
    yield dispatch.connect()

    dispatch.subscriber_add("fera", "service", ["name", "display_name", "latent_sessions_count", "logged_sessions_count"])
    #dispatch.subscriber_add("fera", "session", ["name", "login", "last_task_display_name", "last_task_event_date"])

@defer.inlineCallbacks
def test2():
    head = HeadClient("voice.apiest.com", 20000)
    yield head.connect()

    result = yield head.list("/proc/localhost")
    log.debug("head.list(): %s" % result)

    resultdispatch = yield head.get("/proc/"+result[0]+"/Head_IVMID/Dispatch")
    log.debug("head.get(): (port) %s" % resultdispatch.port)

    dispatch = DispatchClient("voice.apiest.com", resultdispatch.port)
    yield dispatch.connect()

    dispatch.subscriber_add("fera", "service", ["name", "display_name", "latent_sessions_count", "logged_sessions_count"])
    dispatch.subscriber_add("fera", "session", ["name", "login", "last_task_display_name", "last_task_event_date", "lost_inbound.count('0')"])

    #resultccxml = yield head.get("/proc/"+result[0]+"/Head_IVMID/Ccxml")
    #log.debug("head.get(): (port) %s" % resultccxml.port)

    #ccxml = CcxmlClient("voice.apiest.com", resultccxml.port)
    #yield ccxml.connect()

    #reactor.callLater(2, ccxml.send_login, 1, "gric", "autopass")

if __name__ == "__main__":

    from twisted.python.log import startLogging
    from sys import stdout
    startLogging(stdout)

    log.debug("Async")
    
    reactor.callWhenRunning(do_init)
    reactor.run()
