policy_assignment_pipeline = [
    {"$addFields": {
        "meta": {"$function": {
            "body": """function() {
                var purposes = ["research", "administration", "marketing", "sales", "development", "testing", "customer support"];
                var meta = {"aip": [], "pip": []};
                var usedPurposes = new Set();
                var has_policy = Math.random() < 0.5;  // 50% probability to have at least one policy
                if (has_policy) {
                    var num_policies = Math.floor(Math.random() * 3) + 1;  // From 1 to 3 policies
                    for (var i = 0; i < num_policies; i++) {
                        var is_positive = Math.random() < 0.5;
                        var purpose;
                        do {
                            purpose = purposes[Math.floor(Math.random() * purposes.length)];
                        } while (usedPurposes.has(purpose));
                        usedPurposes.add(purpose);
                        if (is_positive) {
                            meta.aip.push(purpose);
                        } else {
                            meta.pip.push(purpose);
                        }
                    }
                }
                return meta;
            }""",
            "args": [],
            "lang": "js"
        }},
        "pol": {"$function": {
            "body": """function(meta) {
                var policies = [];
                if (meta.aip.length > 0) {
                    policies.push({
                        exp: "s.ap in meta.aip",
                        tp: "positive"
                    });
                }
                if (meta.pip.length > 0) {
                    policies.push({
                        exp: "s.ap in meta.pip",
                        tp: "negative"
                    });
                }
                return policies;
            }""",
            "args": ["$meta"],
            "lang": "js"
        }}
    }}
]
