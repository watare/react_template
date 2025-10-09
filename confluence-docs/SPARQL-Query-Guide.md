# SPARQL Query Guide - IED Explorer

**Space**: VPAC
**Category**: Technical Reference
**Last Updated**: 2025-01-09

---

## Introduction

This guide documents all SPARQL queries used in the IED Explorer feature, with explanations for beginners and advanced optimization tips.

---

## Table of Contents

1. [SPARQL Basics](#sparql-basics)
2. [IED List Queries](#ied-list-queries)
3. [IED Hierarchy Queries](#ied-hierarchy-queries)
4. [Query Optimization](#query-optimization)
5. [Testing Queries in Fuseki](#testing-queries-in-fuseki)

---

## SPARQL Basics

### What is SPARQL?

**SPARQL** (SPARQL Protocol and RDF Query Language) is a query language for RDF databases, similar to SQL for relational databases.

### Basic Structure

```sparql
PREFIX prefix: <http://example.com/namespace#>

SELECT ?variable1 ?variable2
WHERE {
  ?subject predicate ?object .
  ?subject prefix:property ?variable1 .
  OPTIONAL { ?subject prefix:optional ?variable2 }
  FILTER(condition)
}
ORDER BY ?variable1
LIMIT 100
```

### Key Components

| Component | Purpose | Example |
|-----------|---------|---------|
| PREFIX | Define namespace shortcuts | `PREFIX iec: <http://iec61850.com/SCL#>` |
| SELECT | Specify which variables to return | `SELECT ?ied ?name ?type` |
| WHERE | Graph pattern to match | `{ ?ied rdf:type iec:IED }` |
| OPTIONAL | Match pattern if exists, but don't require it | `OPTIONAL { ?ied iec:desc ?desc }` |
| FILTER | Filter results by condition | `FILTER(CONTAINS(?name, "BCU"))` |
| ORDER BY | Sort results | `ORDER BY ?name` |
| LIMIT | Limit number of results | `LIMIT 1000` |

### Common Prefixes

```sparql
PREFIX iec: <http://iec61850.com/SCL#>        # IEC 61850 ontology
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>  # RDF standard
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>       # RDF Schema
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>            # XML datatypes
```

---

## IED List Queries

### Query 1: Get All IEDs (Group by Type)

**Purpose**: List all IEDs with basic metadata, grouped by type (BCU, SCU, etc.)

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?ied ?name ?type ?manufacturer ?desc
WHERE {
  ?ied rdf:type iec:IED .
  OPTIONAL { ?ied iec:name ?name }
  OPTIONAL { ?ied iec:type ?type }
  OPTIONAL { ?ied iec:manufacturer ?manufacturer }
  OPTIONAL { ?ied iec:desc ?desc }
}
ORDER BY ?type ?name
LIMIT 1000
```

**Explanation**:

1. `?ied rdf:type iec:IED` - Find all resources of type IED
2. `OPTIONAL` - Get these properties if they exist (some IEDs may not have descriptions)
3. `ORDER BY ?type ?name` - Sort by type first (BCU, SCU), then by name
4. `LIMIT 1000` - Safety limit to prevent huge result sets

**With Search Filter**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?ied ?name ?type ?manufacturer ?desc
WHERE {
  ?ied rdf:type iec:IED .
  OPTIONAL { ?ied iec:name ?name }
  OPTIONAL { ?ied iec:type ?type }
  OPTIONAL { ?ied iec:manufacturer ?manufacturer }
  OPTIONAL { ?ied iec:desc ?desc }
  FILTER(CONTAINS(LCASE(?name), LCASE("BCU")))
}
ORDER BY ?type ?name
LIMIT 1000
```

**New Parts**:
- `FILTER(CONTAINS(LCASE(?name), LCASE("BCU")))` - Case-insensitive search for "BCU" in name
- `LCASE()` - Converts to lowercase for case-insensitive comparison

---

### Query 2: Get IEDs Grouped by Bay

**Purpose**: List IEDs with their associated bay (physical location in substation)

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?ied ?iedName ?type ?manufacturer ?bay ?bayName
WHERE {
  ?ied rdf:type iec:IED .
  ?ied iec:name ?iedName .
  OPTIONAL { ?ied iec:type ?type }
  OPTIONAL { ?ied iec:manufacturer ?manufacturer }

  # Try to find associated bay through LNode references
  OPTIONAL {
    ?lNode iec:iedName ?iedName .
    ?bay iec:hasLNode ?lNode .
    ?bay rdf:type iec:Bay .
    OPTIONAL { ?bay iec:name ?bayName }
  }
}
ORDER BY ?bayName ?iedName
LIMIT 1000
```

**Explanation**:

1. Get all IEDs as before
2. `OPTIONAL { ... }` - Try to find bay association
3. `?lNode iec:iedName ?iedName` - Find LNodes that reference this IED by name
4. `?bay iec:hasLNode ?lNode` - Find Bay that contains this LNode
5. `?bay rdf:type iec:Bay` - Verify it's actually a Bay
6. Result: IEDs without bay association will have null `bayName`

**Grouping Logic (Python)**:

```python
grouped = {}
for binding in results:
    bay_name = extract_binding_value(binding.get("bayName"))
    if not bay_name:
        bay_name = "Unknown"

    if bay_name not in grouped:
        grouped[bay_name] = []

    grouped[bay_name].append({
        "uri": extract_binding_value(binding.get("ied")),
        "name": extract_binding_value(binding.get("iedName")),
        ...
    })
```

---

## IED Hierarchy Queries

### Query 3: Get AccessPoints (IED Children)

**Purpose**: Get all AccessPoints for a specific IED

**Parent Type**: IED

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?name ?type
WHERE {
  <http://example.com/SCL#IED_BCU1> iec:hasAccessPoint ?child .
  OPTIONAL { ?child iec:name ?name }
  BIND("AccessPoint" as ?type)
}
```

**Explanation**:

1. `<http://example.com/SCL#IED_BCU1>` - Specific IED URI (hardcoded in query)
2. `iec:hasAccessPoint ?child` - Find all AccessPoints
3. `BIND("AccessPoint" as ?type)` - Set type for all results
4. Result: List of AccessPoint URIs with names

**Display Name**: Use `?name` directly (e.g., "PROCESS_AP")

---

### Query 4: Get Server (AccessPoint Child)

**Purpose**: Get Server for a specific AccessPoint

**Parent Type**: AccessPoint

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?name ?type
WHERE {
  <http://example.com/SCL#AccessPoint1> iec:hasServer ?child .
  BIND("Server" as ?name)
  BIND("Server" as ?type)
}
```

**Explanation**:

1. AccessPoints typically have exactly 1 Server
2. `BIND("Server" as ?name)` - Server rarely has a specific name, so we use "Server"

**Display Name**: "Server"

---

### Query 5: Get LDevices (Server Children)

**Purpose**: Get all Logical Devices for a specific Server

**Parent Type**: Server

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?inst ?ldName ?type
WHERE {
  <http://example.com/SCL#Server1> iec:hasLDevice ?child .
  OPTIONAL { ?child iec:inst ?inst }
  OPTIONAL { ?child iec:ldName ?ldName }
  BIND("LDevice" as ?type)
}
```

**Explanation**:

1. `iec:inst` - LDevice instance identifier (e.g., "LDAGSA1")
2. `iec:ldName` - Optional descriptive name (e.g., "AgentServerLD")

**Display Name**: `"{inst} ({ldName})"` or just `"{inst}"` if no ldName
- Example: "LDAGSA1 (AgentServerLD)"
- Example: "LDAGSA1"

---

### Query 6: Get Logical Nodes (LDevice Children)

**Purpose**: Get all Logical Nodes (LN0 and LN) for a specific LDevice

**Parent Type**: LDevice

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?lnClass ?lnType ?prefix ?inst ?type
WHERE {
  {
    <http://example.com/SCL#LDevice1> iec:hasLN0 ?child .
    BIND("LN0" as ?type)
  } UNION {
    <http://example.com/SCL#LDevice1> iec:hasLN ?child .
    BIND("LN" as ?type)
  }
  OPTIONAL { ?child iec:lnClass ?lnClass }
  OPTIONAL { ?child iec:lnType ?lnType }
  OPTIONAL { ?child iec:prefix ?prefix }
  OPTIONAL { ?child iec:inst ?inst }
}
ORDER BY ?type ?lnClass ?inst
```

**Explanation**:

1. `{ ... } UNION { ... }` - Match either LN0 or LN
2. LN0 is special (unique in each LDevice), LN can be multiple
3. `iec:lnClass` - Logical node class (LPHD, XCBR, TCTR, etc.)
4. `iec:prefix` - Optional prefix (e.g., "I01A")
5. `iec:inst` - Instance number (e.g., "0", "11")

**Display Name**: `"{prefix}{lnClass}{inst}"`
- Example: "LPHD0" (prefix=empty, lnClass=LPHD, inst=0)
- Example: "I01ATCTR11" (prefix=I01A, lnClass=TCTR, inst=11)

**Logic**:

```python
name_parts = []
if prefix:
    name_parts.append(prefix)
if lnClass:
    name_parts.append(lnClass)
if inst:
    name_parts.append(inst)
node["name"] = "".join(name_parts) if name_parts else "Unknown LN"
```

---

### Query 7: Get LN0 Children (DataSets, Controls, DOI)

**Purpose**: Get all children of LN0 (data organization and communication controls)

**Parent Type**: LN0

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?name ?type ?category
WHERE {
  {
    <http://example.com/SCL#LN0_1> iec:hasDataSet ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("DataSet" as ?type)
    BIND("data" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasGSEControl ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("GSEControl" as ?type)
    BIND("communication" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasSampledValueControl ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("SampledValueControl" as ?type)
    BIND("communication" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasReportControl ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("ReportControl" as ?type)
    BIND("communication" as ?category)
  } UNION {
    <http://example.com/SCL#LN0_1> iec:hasDOI ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("DOI" as ?type)
    BIND("data" as ?category)
  }
}
ORDER BY ?category ?type ?name
```

**Explanation**:

1. Multiple UNION blocks to check for different child types
2. `?category` - Groups results: "data", "communication", "inputs"
3. Ordered by category first, then type, then name

**Node Types**:

| Type | Category | Description | Expandable |
|------|----------|-------------|------------|
| DataSet | data | Group of data attributes | Yes |
| GSEControl | communication | GOOSE control block | No |
| SampledValueControl | communication | Sampled values control | No |
| ReportControl | communication | Report control block | No |
| DOI | data | Data object instance | No |

**Display Name**: Use `?name` directly

---

### Query 8: Get LN Children (DOI, Inputs)

**Purpose**: Get children of regular Logical Nodes

**Parent Type**: LN

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?name ?type ?category
WHERE {
  {
    <http://example.com/SCL#LN_1> iec:hasDOI ?child .
    OPTIONAL { ?child iec:name ?name }
    BIND("DOI" as ?type)
    BIND("data" as ?category)
  } UNION {
    <http://example.com/SCL#LN_1> iec:hasInputs ?child .
    BIND("Inputs" as ?name)
    BIND("Inputs" as ?type)
    BIND("inputs" as ?category)
  }
}
ORDER BY ?category ?type ?name
```

**Explanation**:

1. LN can have DOI (data instances) and Inputs (external references)
2. Inputs typically doesn't have a name, so we bind it to "Inputs"

**Display Name**: Use `?name`

---

### Query 9: Get DataSet Children (FCDA)

**Purpose**: Get all Functional Constraint Data Attributes in a DataSet

**Parent Type**: DataSet

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?ldInst ?prefix ?lnClass ?lnInst ?doName ?daName ?fc ?type
WHERE {
  <http://example.com/SCL#DataSet1> iec:hasFCDA ?child .
  OPTIONAL { ?child iec:ldInst ?ldInst }
  OPTIONAL { ?child iec:prefix ?prefix }
  OPTIONAL { ?child iec:lnClass ?lnClass }
  OPTIONAL { ?child iec:lnInst ?lnInst }
  OPTIONAL { ?child iec:doName ?doName }
  OPTIONAL { ?child iec:daName ?daName }
  OPTIONAL { ?child iec:fc ?fc }
  BIND("FCDA" as ?type)
}
```

**Explanation**:

1. FCDA is a reference to a data attribute in the IED's data model
2. Components:
   - `ldInst` - Logical Device instance
   - `prefix`, `lnClass`, `lnInst` - Logical Node reference
   - `doName` - Data Object name
   - `daName` - Data Attribute name
   - `fc` - Functional Constraint (ST, MX, CF, etc.)

**Display Name**: `"{ldInst}.{prefix}{lnClass}{lnInst}.{doName}.{daName} [{fc}]"`
- Example: "LDAGSA1.LPHD0.PhyHealth.stVal [ST]"

**Logic**:

```python
parts = []
if ldInst:
    parts.append(ldInst)

ln_parts = []
if prefix:
    ln_parts.append(prefix)
if lnClass:
    ln_parts.append(lnClass)
if lnInst:
    ln_parts.append(lnInst)
if ln_parts:
    parts.append("".join(ln_parts))

if doName:
    parts.append(doName)
if daName:
    parts.append(daName)

fc_suffix = f" [{fc}]" if fc else ""
node["name"] = ".".join(parts) + fc_suffix
```

---

### Query 10: Get Inputs Children (ExtRef)

**Purpose**: Get all External References in an Inputs block

**Parent Type**: Inputs

**Query**:

```sparql
PREFIX iec: <http://iec61850.com/SCL#>
SELECT ?child ?iedName ?ldInst ?prefix ?lnClass ?lnInst ?doName ?daName ?type
WHERE {
  <http://example.com/SCL#Inputs1> iec:hasExtRef ?child .
  OPTIONAL { ?child iec:iedName ?iedName }
  OPTIONAL { ?child iec:ldInst ?ldInst }
  OPTIONAL { ?child iec:prefix ?prefix }
  OPTIONAL { ?child iec:lnClass ?lnClass }
  OPTIONAL { ?child iec:lnInst ?lnInst }
  OPTIONAL { ?child iec:doName ?doName }
  OPTIONAL { ?child iec:daName ?daName }
  BIND("ExtRef" as ?type)
}
```

**Explanation**:

1. ExtRef is a reference to data from another IED (input binding)
2. Similar to FCDA but includes `iedName` to specify source IED

**Display Name**: `"{iedName}/{ldInst}/{prefix}{lnClass}{lnInst}/{doName}/{daName}"`
- Example: "POSTE4/LDAGSA1/LPHD0/PhyHealth/stVal"

**Logic**:

```python
parts = []
if iedName:
    parts.append(iedName)
if ldInst:
    parts.append(ldInst)

ln_parts = []
if prefix:
    ln_parts.append(prefix)
if lnClass:
    ln_parts.append(lnClass)
if lnInst:
    ln_parts.append(lnInst)
if ln_parts:
    parts.append("".join(ln_parts))

if doName:
    parts.append(doName)
if daName:
    parts.append(daName)

node["name"] = "/".join(parts)
```

---

## Query Optimization

### 1. Use DISTINCT Wisely

**Bad**:
```sparql
SELECT DISTINCT ?ied ?name ?type
WHERE {
  ?ied rdf:type iec:IED .
  ?ied iec:name ?name .
  ?ied iec:type ?type .
}
```

If there are duplicate triples, DISTINCT forces deduplication, which is expensive.

**Good**:
```sparql
SELECT ?ied ?name ?type
WHERE {
  ?ied rdf:type iec:IED .
  ?ied iec:name ?name .
  ?ied iec:type ?type .
}
```

Only use DISTINCT if you expect and need to remove duplicates.

---

### 2. Order of Triple Patterns

**Bad** (starts with OPTIONAL):
```sparql
WHERE {
  OPTIONAL { ?ied iec:name ?name }
  ?ied rdf:type iec:IED .
}
```

**Good** (required patterns first):
```sparql
WHERE {
  ?ied rdf:type iec:IED .
  OPTIONAL { ?ied iec:name ?name }
}
```

**Why**: Query optimizer starts with required patterns (smaller result set), then adds optional data.

---

### 3. Limit Early

**Bad**:
```sparql
SELECT ?ied ?name
WHERE {
  ?ied rdf:type iec:IED .
  ?ied iec:name ?name .
}
ORDER BY ?name
LIMIT 100
```

**Better**:
```sparql
SELECT ?ied ?name
WHERE {
  {
    SELECT ?ied
    WHERE {
      ?ied rdf:type iec:IED .
    }
    LIMIT 100
  }
  ?ied iec:name ?name .
}
ORDER BY ?name
```

**Why**: Limits the number of IEDs before fetching names, reducing work.

---

### 4. Use FILTER at the End

**Bad**:
```sparql
WHERE {
  FILTER(CONTAINS(?name, "BCU"))
  ?ied rdf:type iec:IED .
  ?ied iec:name ?name .
}
```

**Good**:
```sparql
WHERE {
  ?ied rdf:type iec:IED .
  ?ied iec:name ?name .
  FILTER(CONTAINS(?name, "BCU"))
}
```

**Why**: Fetch all data first, then filter. Optimizer can apply filter efficiently at the end.

---

### 5. Avoid Cartesian Products

**Bad**:
```sparql
WHERE {
  ?ied rdf:type iec:IED .
  ?ap rdf:type iec:AccessPoint .
}
```

**Result**: Every IED × Every AccessPoint (huge result set!)

**Good**:
```sparql
WHERE {
  ?ied rdf:type iec:IED .
  ?ied iec:hasAccessPoint ?ap .
  ?ap rdf:type iec:AccessPoint .
}
```

**Why**: Always connect variables with predicates.

---

### 6. Use Property Paths

**Long Version**:
```sparql
WHERE {
  ?ied iec:hasAccessPoint ?ap .
  ?ap iec:hasServer ?server .
  ?server iec:hasLDevice ?ld .
}
```

**Short Version**:
```sparql
WHERE {
  ?ied iec:hasAccessPoint/iec:hasServer/iec:hasLDevice ?ld .
}
```

**Why**: More concise, but use with caution (can be slower for complex paths).

---

## Testing Queries in Fuseki

### 1. Access Fuseki UI

Navigate to: http://localhost:3030

### 2. Select Dataset

Click on your dataset (e.g., `SCD_POSTE_V1`)

### 3. Go to Query Tab

Click "query" in the left sidebar

### 4. Paste Query

Paste your SPARQL query in the text area

### 5. Execute

Click "Run Query" button

### 6. View Results

Results appear in a table below the query editor

### 7. Format Results

Click "Format" button to format JSON results

### 8. Export Results

Click "Export" to save results as CSV or JSON

---

## Common Issues and Solutions

### Issue 1: Empty Results

**Symptom**: Query returns 0 results

**Possible Causes**:
1. Wrong dataset selected
2. Wrong namespace/prefix
3. Data doesn't exist
4. Typo in property name

**Solution**:
```sparql
# Check what types exist
SELECT DISTINCT ?type
WHERE {
  ?s rdf:type ?type .
}
LIMIT 100

# Check what properties exist
SELECT DISTINCT ?p
WHERE {
  ?s ?p ?o .
}
LIMIT 100

# Check IED namespace
SELECT ?ied
WHERE {
  ?ied rdf:type <http://iec61850.com/SCL#IED> .
}
LIMIT 10
```

---

### Issue 2: Query Timeout

**Symptom**: "Query execution time exceeded"

**Possible Causes**:
1. Query too complex
2. Cartesian product
3. Missing LIMIT

**Solution**:
- Add LIMIT 1000
- Break into smaller queries
- Check for Cartesian products
- Add more specific filters

---

### Issue 3: Wrong Display Names

**Symptom**: Shows URI instead of name

**Cause**: Using wrong variable

**Solution**:
```sparql
# Wrong
SELECT ?child
WHERE {
  ?parent iec:hasChild ?child .
}

# Right
SELECT ?child ?name
WHERE {
  ?parent iec:hasChild ?child .
  OPTIONAL { ?child iec:name ?name }
}
```

---

## Best Practices Summary

1. ✅ Always use LIMIT for safety
2. ✅ Put required patterns before OPTIONAL
3. ✅ Use FILTER at the end of WHERE block
4. ✅ Test queries in Fuseki UI first
5. ✅ Use meaningful variable names (?ied not ?x)
6. ✅ Add comments for complex queries
7. ✅ Use OPTIONAL for properties that may not exist
8. ✅ Connect all variables with predicates (avoid Cartesian products)

---

## Related Documentation

- [IED Explorer Overview](./IED-Explorer-Overview.md)
- [API Endpoints Reference](./API-Endpoints-Reference.md)
- [RDF/SPARQL Tutorial](https://www.w3.org/TR/sparql11-query/)

---

**End of SPARQL Query Guide**
