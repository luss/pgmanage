
//TODO: move these constants to constants.js file
/// <summary>
/// Transaction codes of client requests.
/// </summary>
var v_queryRequestCodes = {
	Login: 0,
	Query: 1,
	Execute: 2,
	Script: 3,
	QueryEditData: 4,
	QueryEditDataNew: 40,
	SaveEditData: 5,
	SaveEditDataNew: 55,
	CancelThread: 6,
	Debug: 7,
	CloseTab: 8,
	AdvancedObjectSearch: 9,
	Console: 10,
	Terminal: 11,
	Ping: 12
}

/// <summary>
/// Transaction codes of server responses.
/// </summary>
var v_queryResponseCodes = {
	LoginResult: 0,
	QueryResult: 1,
	QueryEditDataResult: 2,
	SaveEditDataResult: 3,
	SaveEditDataResultNew: 33,
	SessionMissing: 4,
	PasswordRequired: 5,
	QueryAck: 6,
	MessageException: 7,
	DebugResponse: 8,
	RemoveContext: 9,
	AdvancedObjectSearchResult: 10,
	ConsoleResult: 11,
	TerminalResult: 12,
	Pong: 13
}

//Adding padLeft function to Number
Number.prototype.padLeft = function(base,chr){
    var  len = (String(base || 10).length - String(this).length)+1;
    return len > 0? new Array(len).join(chr || '0')+this : this;
}

export {
  v_queryRequestCodes,
  v_queryResponseCodes,
};