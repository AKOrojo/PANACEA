import uuid

map_function = """
function() {
    function generateId() {
        return (UUID());
    }
    function duMapper(cPath, obj) {
        var urpS = [];
        for (var f in obj) {
            var v = obj[f];
            var urp = {path: cPath.slice(), id: generateId(), K: f};
            if (typeof v === 'object' && v !== null) {
                var sPath = cPath.slice();
                sPath.push(urp.id);
                var sUrpS = duMapper(sPath, v);
                urpS = urpS.concat(sUrpS);
            } else {
                urp.V = v;
            }
            urpS.push(urp);
        }
        return urpS;
    }
    var urpS = duMapper([this._id], this);
    for (var i = 0; i < urpS.length; i++) {
        emit(urpS[i].id, urpS[i]);
    }
}
"""

reduce_function = """
function(key, values) {
    return values[0];
}
"""
