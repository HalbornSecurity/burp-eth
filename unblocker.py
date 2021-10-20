from render import EthereumMainPanel
from burp import IBurpExtender
from burp import ITab

class BurpExtender(IBurpExtender, ITab):
    def registerExtenderCallbacks(self, callbacks):
        # keep a reference to our callbacks object
        self._callbacks = callbacks
        
        # obtain an extension helpers object
        self._helpers = callbacks.getHelpers()
        
        # set our extension name
        callbacks.setExtensionName("Unblocker")
        
        ethereum_main_panel = EthereumMainPanel().get()
        
        # set the Ethereum panel as default for now
        self._main_pane = ethereum_main_panel

        # customize our UI components
        callbacks.customizeUiComponent(self._main_pane)
        
        # add the custom tab to Burp's UI
        callbacks.addSuiteTab(self)

        return

    #
    # implement ITab
    #
    
    def getTabCaption(self):
        return "Unblocker"
    
    def getUiComponent(self):
        return self._main_pane