arc = ...  # Define the value for arc
co = ...  # Define the value for co
crs = ...  # Define the value for crs
ppc = ...  # Define the value for ppc
st = ...  # Define the value for st

combined_pipeline = [
    {"$addFields": {"urpS": {"$function": {
        "body": """function(doc) {
            function generateId() { return (UUID()); }
            function duMapper(cPath, obj) {
                var urpS = [];
                function getRandomPoliciesAndMeta() {
                    var purposes = ["research", "administration", "marketing", "sales", "development", "testing", "customer support"];
                    var policies = [];
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
                    return {policies: policies, meta: meta};
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
                    var {policies, meta} = getRandomPoliciesAndMeta();
                    urp.meta = meta;
                    urp.pol = policies;
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

combined_pipeline_projector = [
    {
        "$addFields": {
            "urpS": {
                "$function": {
                    "body": """function(doc) {
                        function generateId() { return UUID(); }
                        function duMapper(cPath, obj) {
                            var urpS = [];
                            function getRandomPoliciesAndMeta() {
                                var purposes = ["research", "administration", "marketing", "sales", "development", "testing", "customer support"];
                                var policies = [];
                                var meta = {"aip": [], "pip": []};
                                var usedPurposes = new Set();
                                var has_policy = Math.random() < 0.5; // 50% probability to have at least one policy
                                if (has_policy) {
                                    var num_policies = Math.floor(Math.random() * 3) + 1; // From 1 to 3 policies
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
                                return { policies: policies, meta: meta };
                            }
                            for (var f in obj) {
                                var v = obj[f];
                                var urp = { path: cPath.slice(), id: generateId(), K: f };
                                if (typeof v === 'object' && v !== null) {
                                    var sPath = cPath.slice();
                                    sPath.push(urp.id);
                                    var sUrpS = duMapper(sPath, v);
                                    urpS = urpS.concat(sUrpS);
                                } else {
                                    urp.V = v;
                                }
                                var { policies, meta } = getRandomPoliciesAndMeta();
                                urp.meta = meta;
                                urp.pol = policies;
                                urpS.push(urp);
                            }
                            return urpS;
                        }
                        return duMapper([doc._id], doc);
                    }""",
                    "args": ["$$ROOT"],
                    "lang": "js"
                }
            }
        }
    },
    { "$unwind": "$urpS" },
    {
        "$group": {
            "_id": "$urpS.id",
            "urp": { "$first": "$urpS" }
        }
    },
    { "$replaceRoot": { "newRoot": "$urp" } },
    {
        "$group": {
            "_id": { "$arrayElemAt": ["$path", 0] },
            "urps": {
                "$push": {
                    "id": "$id",
                    "value": "$$ROOT"
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "key": "$_id",
            "urps": 1
        }
    },
    {
        "$project": {
            "mapped_documents": {
                "$map": {
                    "input": "$urps",
                    "as": "urp",
                    "in": {
                        "$arrayToObject": [
                            [
                                {
                                    "k": { "$arrayElemAt": ["$$urp.value.path", -1] },
                                    "v": "$$urp.value"
                                }
                            ]
                        ]
                    }
                }
            },
            "key": 1
        }
    },
    {
        "$project": {
            "sec_map_dus": {
                "$arrayToObject": [
                    [
                        {
                            "k": "$key",
                            "v": "$mapped_documents"
                        }
                    ]
                ]
            }
        }
    },
    {
        "$project": {
            "sec_reduces_data_units": {
                "$arrayToObject": [
                    {
                        "$map": {
                            "input": { "$objectToArray": "$sec_map_dus" },
                            "as": "du",
                            "in": {
                                "k": "$$du.k",
                                "v": {
                                    "$function": {
                                        "body": """function(urpS, key) {
                                            var du = {};
                                            var tbs = [];
                                            var tbp = [];
                                            var meta = [];
                                            var pol = [];
                                            for (var i = 0; i < urpS.length; i++) {
                                                var urp = urpS[i].value;
                                                if (urp.path[urp.path.length - 1] === key) {
                                                    if (urp.hasOwnProperty('V')) {
                                                        du[urp.K] = urp.V;
                                                    } else {
                                                        du[urp.K] = urp.id;
                                                        tbs.push(urp.id);
                                                    }
                                                } else {
                                                    if (!du.hasOwnProperty(urp.path[urp.path.length - 1])) {
                                                        du[urp.path[urp.path.length - 1]] = {};
                                                        tbp.push(urp.path[urp.path.length - 1]);
                                                    }
                                                    if (urp.hasOwnProperty('V')) {
                                                        du[urp.path[urp.path.length - 1]][urp.K] = urp.V;
                                                    } else {
                                                        du[urp.path[urp.path.length - 1]][urp.K] = urp.id;
                                                        tbs.push(urp.id);
                                                    }
                                                }
                                                if (urp.hasOwnProperty('meta')) {
                                                    meta.push({
                                                        id: urp.id,
                                                        path: urp.path,
                                                        psSet: urp.meta
                                                    });
                                                }
                                                if (urp.hasOwnProperty('pol')) {
                                                    pol.push({
                                                        id: urp.id,
                                                        K: urp.K,
                                                        path: urp.path,
                                                        psa: urp.pol.filter(function(policy) { return policy.tp === 'positive'; }).map(function(policy) { return policy.exp; }),
                                                        psp: urp.pol.filter(function(policy) { return policy.tp === 'negative'; }).map(function(policy) { return policy.exp; })
                                                    });
                                                }
                                            }
                                            du.tbs = tbs;
                                            du.tbp = tbp;
                                            du.meta = meta;
                                            du.pol = pol;
                                            return du;
                                        }""",
                                        "args": ["$$du.v", "$$du.k"],
                                        "lang": "js"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    },
    {
        "$project": {
            "sec_finalized_data_units": {
                "$arrayToObject": [
                    {
                        "$map": {
                            "input": { "$objectToArray": "$sec_reduces_data_units" },
                            "as": "du",
                            "in": {
                                "k": "$$du.k",
                                "v": {
                                    "$function": {
                                        "body": """function(du, arc, co, crs, ppc, st) {
                                            if (du.hasOwnProperty('tbs')) {
                                                for (var i = 0; i < du.tbs.length; i++) {
                                                    var oid = du.tbs[i];
                                                    if (du.hasOwnProperty(oid)) {
                                                        updateDu(du, oid, du[oid]);
                                                        delete du[oid];
                                                    }
                                                }
                                                delete du.tbs;
                                            }
                                            if (du.hasOwnProperty('tbp')) {
                                                for (var i = 0; i < du.tbp.length; i++) {
                                                    var oid = du.tbp[i];
                                                    if (du.hasOwnProperty(oid)) {
                                                        delete du[oid];
                                                    }
                                                }
                                                delete du.tbp;
                                            }
                                            var authS = [];
                                            var prohS = [];
                                            for (var i = 0; i < du.pol.length; i++) {
                                                var p = du.pol[i];
                                                var obj = { id: p.id, path: p.path };
                                                if (du.hasOwnProperty('meta')) {
                                                    for (var j = 0; j < du.meta.length; j++) {
                                                        var meta = du.meta[j];
                                                        if (meta.id === p.id && meta.path === p.path) {
                                                            obj.psSet = meta.psSet;
                                                            break;
                                                        }
                                                    }
                                                }
                                                var psa_decisions = p.psa.length === 0 ? [{ set_0: { decision: 'permit', tp: 'positive' } }] :
                                                    p.psa.map(function(psa) {
                                                        return evaluate({ meta: obj, pol: [{ exp: psa, tp: 'positive' }] }, arc);
                                                    });
                                                var psp_decisions = p.psp.length === 0 ? [{ set_0: { decision: 'permit', tp: 'negative' } }] :
                                                    p.psp.map(function(psp) {
                                                        return evaluate({ meta: obj, pol: [{ exp: psp, tp: 'negative' }] }, arc);
                                                    });
                                                var combined_psa = combinePs(psa_decisions.reduce(function(acc, d, i) {
                                                    acc['set_' + i] = d.set_0;
                                                    return acc;
                                                }, {}), co);
                                                var combined_psp = combinePs(psp_decisions.reduce(function(acc, d, i) {
                                                    acc['set_' + i] = d.set_0;
                                                    return acc;
                                                }, {}), co);
                                                var decision = conflictRes({
                                                    positive: combined_psa.positive,
                                                    negative: combined_psp.negative
                                                }, crs);
                                                if (decision === 'permit') {
                                                    authS.push({ id: p.id, path: p.path });
                                                } else if (decision === 'deny') {
                                                    prohS.push({ id: p.id, path: p.path });
                                                } else {
                                                    print("no decision");
                                                }
                                            }
                                            du.authS = authS;
                                            du.prohS = prohS;
                                            var propagated_decision = propagateDCG(du, arc, co, crs, ppc, st);
                                            propagateDFG(du, propagated_decision, ppc, crs, st);
                                            var view = generateView(du);
                                            return view;
                                        }""",
                                        "args": ["$$du.v", arc, co, crs, ppc, st],
                                        "lang": "js"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }
]
