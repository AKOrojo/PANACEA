combined_pipeline = [
    {"$addFields": {"urpS": {"$function": {
        "body": """function(doc) {
            function generateId() { return (UUID()); }
            function duMapper(cPath, obj) {
                var urpS = [];
                function getRandomPolicies() {
                    var purposes = ["research", "administration", "marketing", "sales", "development", "testing", "customer support"];
                    var policies = [];
                    var has_policy = Math.random() < 0.5;  // 50% probability to have at least one policy
                    if (has_policy) {
                        var num_policies = Math.floor(Math.random() * 3) + 1;  // From 1 to 3 policies
                        for (var i = 0; i < num_policies; i++) {
                            var is_positive = Math.random() < 0.5;
                            var purpose = purposes[Math.floor(Math.random() * purposes.length)];
                            var policy = {
                                exp: "s.ap in meta." + purpose,
                                tp: is_positive ? "positive" : "negative"
                            };
                            policies.push(policy);
                        }
                    }
                    return policies;
                }
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
                    urp.meta = [
                        {"research": ["allowed"]}, {"administration": ["allowed"]}, {"marketing": ["allowed"]},
                        {"sales": ["allowed"]}, {"development": ["allowed"]}, {"testing": ["allowed"]}, {"customer support": ["allowed"]}
                    ];
                    urp.pol = getRandomPolicies();
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
