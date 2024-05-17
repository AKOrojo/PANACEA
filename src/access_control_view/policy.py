policy_assignment_pipeline = [
    {"$addFields": {"urpS": {"$function": {
        "body": """function(urpS) {
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
            for (var i = 0; i < urpS.length; i++) {
                urpS[i].pol = getRandomPolicies();
            }
            return urpS;
        }""",
        "args": ["$$urpS"],
        "lang": "js"
    }}}}
]
