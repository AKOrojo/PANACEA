mapper_pipeline = [
        {"$addFields": {"urpS": {"$function": {
            "body": """function(doc) {
                function generateId() { return (UUID()); }
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
                return duMapper([doc._id], doc);
            }""",
            "args": ["$$ROOT"],
            "lang": "js"
        }}}},
        {"$unwind": "$urpS"},
        {"$group": {
            "_id": "$urpS.id",
            "urp": {"$first": "$urpS"}
        }},
        {"$replaceRoot": {"newRoot": "$urp"}}
    ]
