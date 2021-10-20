import api
from java.awt import Color
from java.awt import Font
from java.awt import Dimension;
from java.awt import GridBagLayout
from java.awt import GridBagConstraints
from java.awt import Color
from java.awt.event import ActionListener
from javax.swing import JTextArea
from javax.swing import BorderFactory
from javax.swing import JComboBox
from javax.swing import JLabel;
from javax.swing import JComboBox;
from javax.swing import JPanel
from javax.swing import JButton

COLOR_BURP_HEADERS = Color(244, 124, 60)

class Selector:
    def __init__(self, items = [], title = None):
        self.__items = items
        self.__element = JComboBox(self.__items)
        self.__title = title

    def get_elements(self):
        return self.__elements

    def set_elements(self, items = []):
        if type(items).__name__ == 'list':
            self.__items = items

    def get(self):
        if self.__title:
            border = BorderFactory.createTitledBorder(self.__title)
            bold_font = border.getTitleFont().deriveFont(Font.BOLD, 12)
            border.setTitleColor(COLOR_BURP_HEADERS)
            border.setTitleFont(bold_font)
            self.__element.setBorder(border)

        return self.__element

class TextEditor:
    __rows = 1
    __columns = 1
    __title = None

    def __init__ (self, rows = None, columns = None, title = None):
        if type(rows).__name__ == 'int' and type(rows).__name__ > 0 and type(columns).__name__ == 'int' and type(columns).__name__ > 0:
            self.__rows = rows
            self.__columns = columns

        text_area = JTextArea(self.__rows, self.__columns)
        text_area.setWrapStyleWord(True)
        text_area.setLineWrap(True)
        text_area.setMinimumSize(Dimension(200, 50))

        if type(title).__name__ == 'str':
            self.__title = title
            border = BorderFactory.createTitledBorder(self.__title)
            bold_font = border.getTitleFont().deriveFont(Font.BOLD, 12)
            border.setTitleColor(COLOR_BURP_HEADERS)
            border.setTitleFont(bold_font)
            text_area.setBorder(border)
        
        self.__editor_pane = text_area

    def get(self):
        return self.__editor_pane

class EthereumMainPanel:
    def __init__(self):
        self._panel = JPanel()

    def get(self):
        self._setup()
        return self._panel

    def _setup(self):
        label_error = JLabel()
        label_error.setForeground(Color.RED)

        dropdown_format = Selector(["eth"], "Protocol").get()
        
        editor_input = TextEditor(6,90, 'input data').get()
        editor_abi = TextEditor(2,90, 'ABI').get()
        editor_output = TextEditor(6,90, 'output').get()
        
        button_encode = JButton("encode")
        button_decode = JButton("decode")

        listener = CommandListener(dropdown_format, editor_input, editor_abi, editor_output, label_error)
        button_encode.addActionListener(listener)
        button_decode.addActionListener(listener)

        self._panel.setLayout(GridBagLayout())

        grid_bag_constraints = GridBagConstraints()

        # all components are horizontal
        grid_bag_constraints.fill = GridBagConstraints.BOTH
        
        # <format> dropdown
        grid_bag_constraints.gridx = 0
        grid_bag_constraints.gridy = 6
        grid_bag_constraints.gridwidth = 20
        grid_bag_constraints.weightx = 1
        grid_bag_constraints.ipady = 5
        self._panel.add(dropdown_format, grid_bag_constraints)

        # messages
        grid_bag_constraints.gridx = 8
        grid_bag_constraints.gridy = 0
        grid_bag_constraints.gridwidth = 4
        grid_bag_constraints.weightx = 1
        grid_bag_constraints.gridheight = 4
        grid_bag_constraints.fill = GridBagConstraints.VERTICAL
        self._panel.add(label_error, grid_bag_constraints)

        # <encode> button
        grid_bag_constraints.gridx = 16
        grid_bag_constraints.gridy = 0
        grid_bag_constraints.gridwidth = 4
        grid_bag_constraints.weightx = 0.5
        grid_bag_constraints.gridheight = 1
        grid_bag_constraints.fill = GridBagConstraints.BOTH
        self._panel.add(button_encode, grid_bag_constraints)

        # <decode> button
        grid_bag_constraints.gridx = 16
        grid_bag_constraints.gridy = 5
        grid_bag_constraints.gridwidth = 4
        grid_bag_constraints.gridheight = 1
        grid_bag_constraints.weightx = 0.5
        self._panel.add(button_decode, grid_bag_constraints)

        # function signature textarea
        grid_bag_constraints.gridx = 0
        grid_bag_constraints.gridy = 7
        grid_bag_constraints.gridwidth = 20
        grid_bag_constraints.gridheight = 2
        self._panel.add(editor_abi, grid_bag_constraints)

        # calldata textarea
        grid_bag_constraints.gridx = 0
        grid_bag_constraints.gridy = 11
        grid_bag_constraints.gridwidth = 20
        grid_bag_constraints.gridheight = 4
        grid_bag_constraints.weighty = 0.2
        self._panel.add(editor_input, grid_bag_constraints)

        # output textarea
        grid_bag_constraints.gridx = 0
        grid_bag_constraints.gridy = 16
        grid_bag_constraints.gridwidth = 20
        grid_bag_constraints.gridheight = 4
        self._panel.add(editor_output, grid_bag_constraints)

class CommandListener(ActionListener):
    def __init__(self, dropdown_format = None, editor_input_data = None, editor_input_abi = None, editor_output_data = None, label_error = None):
        self.__dropdown_format = dropdown_format
        self.__editor_input_data = editor_input_data
        self.__editor_input_abi = editor_input_abi
        self.__editor_output_data = editor_output_data
        self.__label_error = label_error

    def actionPerformed(self, e):
        # clear errors
        self.__label_error.setText('')
        self.__label_error.revalidate()

        command = e.getSource().getText()
        format = self.__dropdown_format.getSelectedItem()
        input_data = self.__editor_input_data.getText() if len(self.__editor_input_data.getText().strip()) > 0 else None
        abi = self.__editor_input_abi.getText() if len(self.__editor_input_abi.getText().strip()) > 0 else None

        arguments = {}
        arguments['input'] = input_data
        arguments['abi'] = abi
        arguments['type'] = 'data'
        results = api.Command.execute(format, command, arguments)

        if not results['error']:
            output_data = ''
            output_abi = ''
            newline = int(len(results['data'].keys()) > 1)

            for signature in results['data'].keys():
                output_abi = "{}{}".format(signature, '\n' * newline)
                try:
                    output_data = "{}{}".format(results['data'][signature], '\n' * newline)
                except Exception as error:
                    print(error)

            # display decode input
            self.__editor_output_data.setText(output_data)
            self.__editor_output_data.revalidate()

            # display signature
            self.__editor_input_abi.setText(output_abi)
            self.__editor_input_abi.revalidate()
        else:
            # display error message
            self.__label_error.setText(results['error'])

            # clear input
            self.__editor_output_data.setText('')
            self.__editor_output_data.revalidate()