/*
    <OUTPUTFILENAME>
    Created <DATE> from:
        Messages = <INPUTFILENAME>
        Template = <TEMPLATEFILENAME>
        Language = <LANGUAGEFILENAME>

                     AUTOGENERATED FILE, DO NOT EDIT

*/
import NetworkHeader from '../headers/Networkheader.js'
import MessageDictionary from '../MessageDictionary.js'

var <MSGNAME> = function(buffer) {
    // have baseclass construct the buffer?
    //Message.call(this, MSG_SIZE);
        
    if (buffer==undefined)
    {
        buffer = new ArrayBuffer(NetworkHeader.prototype.MSG_SIZE+<MSGNAME>.prototype.MSG_SIZE);
        this.m_data = new DataView(buffer, NetworkHeader.prototype.MSG_SIZE);
        this.hdr = new NetworkHeader(buffer);
        this.hdr.SetMessageID(<MSGNAME>.prototype.MSG_ID);
        this.hdr.SetDataLength(buffer.byteLength - NetworkHeader.prototype.MSG_SIZE);
        //this.InitializeTime();
        this.Init();
    }
    else
    {
        this.m_data = new DataView(buffer, NetworkHeader.prototype.MSG_SIZE);
        this.hdr = new NetworkHeader(buffer);
    }
};

// add our class to the dictionary
MessageDictionary[<MSGID>] = <MSGNAME>

// how to make constants?
<MSGNAME>.prototype.MSG_ID = <MSGID>;
<MSGNAME>.prototype.MSG_SIZE = <MSGSIZE>;
<MSGNAME>.prototype.MSG_NAME = "<MSGNAME>";

<MSGNAME>.prototype.MsgName = function(){
    return "<MSGNAME>";
}

<MSGNAME>.prototype.Init = function(){
    <INIT_CODE>
};


// http://stackoverflow.com/a/130572
<ENUMERATIONS>
<ACCESSORS>

// Convert to a javascript object
<MSGNAME>.prototype.toObject = function(){
    ret = {};
    <STRUCTUNPACKING>
    return ret;
}

// Reflection information
<MSGNAME>.prototype.fields = [
    <REFLECTION>
]

// for react-native and node.js, we should set module.exports so our class can be accessed externally
if(typeof module != 'undefined' && typeof module.exports != 'undefined')
    module.exports = <MSGNAME>;
