from datetime import datetime
import time
import quickfix as fix
from termcolor import colored


def LOG_EVENT(msg):
    print(colored(msg, "green"))


def LOG_PACKET(packet):
    print(colored(packet, "yellow"))


class Application(fix.Application):
    orderID = 0
    execID = 0
    isLogon = False

    def __init__(self, settings):
        super(Application, self).__init__()
        self.Settings = settings

    def genOrderID(self):
        self.orderID += 1
        return self.orderID

    def genExecID(self):
        self.execID += 1
        return str(self.execID)

    def onCreate(self, sessionID):
        self.sessionID = sessionID
        LOG_EVENT("Session created. Session: %s" % sessionID)
        return

    def onLogon(self, sessionID):
        self.sessionID = sessionID
        LOG_EVENT("onLogon received from server. Session: %s" % sessionID)
        self.isLogon = True
        return

    def onLogout(self, sessionID):
        LOG_EVENT("onLogout received from server. Session: %s" % sessionID)
        return

    def toAdmin(self, message, sessionID):
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        if msgType.getValue() == fix.MsgType_Logon:
            message.setField(fix.SenderSubID("Test FIX"))
            message.setField(fix.RawData("pass"))

        LOG_EVENT("Sending Admin message to server. Session: %s. Message: %s" % (sessionID, message))

    def toApp(self, message, sessionID):
        LOG_EVENT("Sending Application message to server. Session: %s. Message: %s" % (sessionID, message))
        return

    def fromAdmin(self, message, sessionID):
        LOG_EVENT("Received Admin message from server. Session: %s. Message: %s" % (sessionID, message))
        return

    def fromApp(self, message, sessionID):
        LOG_EVENT("Received Application message to server. Session: %s. Message: %s" % (sessionID, message))
        return

    def newOrderSingle(self):
        try:
            LOG_EVENT("New Order Single")

            orderMsg = fix.Message()

            orderMsg.getHeader().setField(self.sessionID.getBeginString())
            orderMsg.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))
            orderMsg.getHeader().setField(self.sessionID.getSenderCompID())
            orderMsg.getHeader().setField(self.sessionID.getTargetCompID())
            orderMsg.getHeader().setField(fix.MsgSeqNum(self.genOrderID()))
            sendingTime = fix.SendingTime()
            sendingTime.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f"))
            orderMsg.getHeader().setField(sendingTime)

            orderMsg.setField(fix.Account("17018382"))
            orderMsg.setField(fix.ClOrdID(self.genExecID()))
            orderMsg.setField(fix.OrderQty(100))
            orderMsg.setField(fix.OrdType(fix.TriggerOrderType_LIMIT))
            orderMsg.setField(fix.Price(1.216))
            orderMsg.setField(fix.Symbol("X.US.OREURUSD"))
            orderMsg.setField(fix.Side(fix.Side_BUY))
            tranactionTime = fix.TransactTime()
            tranactionTime.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f"))
            orderMsg.setField(tranactionTime)
            orderMsg.setField(fix.OpenClose(fix.OpenClose_OPEN))

            LOG_PACKET(orderMsg.toString())

            fix.Session.sendToTarget(orderMsg, self.sessionID)
        except Exception as e:
            print(e)

    def checkOrderStatus(self):
        try:
            LOG_EVENT("Check Order Status")

            orderMsg = fix.Message()

            orderMsg.getHeader().setField(self.sessionID.getBeginString())
            orderMsg.getHeader().setField(fix.MsgType("UAF"))
            orderMsg.getHeader().setField(self.sessionID.getSenderCompID())
            orderMsg.getHeader().setField(self.sessionID.getTargetCompID())
            orderMsg.getHeader().setField(fix.MsgSeqNum(self.genOrderID()))
            sendingTime = fix.SendingTime()
            sendingTime.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f"))
            orderMsg.getHeader().setField(sendingTime)

            orderMsg.setField(fix.Account("17018382"))
            orderMsg.setField(50584, self.genExecID())

            LOG_PACKET(orderMsg.toString())

            fix.Session.sendToTarget(orderMsg, self.sessionID)
        except Exception as e:
            print(e)

    def checkAccountData(self):
        try:
            LOG_EVENT("Check Account Data")

            orderMsg = fix.Message()

            orderMsg.getHeader().setField(self.sessionID.getBeginString())
            orderMsg.getHeader().setField(fix.MsgType("UAR"))
            orderMsg.getHeader().setField(self.sessionID.getSenderCompID())
            orderMsg.getHeader().setField(self.sessionID.getTargetCompID())
            orderMsg.getHeader().setField(fix.MsgSeqNum(self.genOrderID()))
            sendingTime = fix.SendingTime()
            sendingTime.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f"))
            orderMsg.getHeader().setField(sendingTime)

            orderMsg.setField(fix.Account("17018382"))
            orderMsg.setField(20003, self.genExecID())

            LOG_PACKET(orderMsg.toString())

            fix.Session.sendToTarget(orderMsg, self.sessionID)
        except Exception as e:
            print(e)


try:
    settings = fix.SessionSettings("config.cfg")
    application = Application(settings)

    storeFactory = fix.FileStoreFactory(settings)
    logFactory = fix.ScreenLogFactory(settings)

    initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
    initiator.start()

    bOrderSent = False
    while True:
        time.sleep(10)
        # TODO call send_order
        if bOrderSent == False and application.isLogon == True:
            application.newOrderSingle()
            bOrderSent = True
        # TODO print order status
        application.checkOrderStatus()
        # TODO print account balance every 10 seconds
        application.checkAccountData()

except (fix.ConfigError, fix.RuntimeError) as e:
    print(e)
