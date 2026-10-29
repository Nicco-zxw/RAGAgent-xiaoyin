"""Validate declared conflicts using observed evidence, not invented precedence."""
def matches(citation, read):
    return isinstance(citation, dict) and any(
        all(citation.get(k) == row.get(k) for k in ('document_id','passage_id','version_date'))
        and isinstance(citation.get('quote'), str) and citation['quote']
        and citation['quote'] in row['quote'] for row in read)

def validate_conflicts(result, read, observations):
    errors=[]
    conflicts=result.get('conflicts', [])
    if not isinstance(conflicts,list): return ['conflicts must be list']
    known={r['document_id']+'/'+r['passage_id'] for r in read}
    for conflict in conflicts:
        if not isinstance(conflict,dict): continue
        sources=conflict.get('sources')
        if not isinstance(sources,list) or len(sources)<2 or any(not isinstance(x,str) or x not in known for x in sources):
            errors.append('conflict sources must reference at least two read passages'); continue
        read_steps=[i for i,o in enumerate(observations) if o['action']=='read_passage' and o['result']['ok'] and o['result']['data']['document_id']+'/'+o['result']['data']['passage_id'] in sources]
        # Require a successful supplementary search after both sources were read.
        if not any(i>max(read_steps,default=-1) and o['action']=='search_documents' and o['result']['ok'] for i,o in enumerate(observations)):
            errors.append('Conflict requires supplementary search after reading its sources; search scope, supersession or priority.')
        if conflict.get('resolved') is True:
            citations=conflict.get('resolution_citations')
            if not isinstance(citations,list) or not citations or not all(matches(c,read) for c in citations):
                errors.append('Resolved conflict requires resolution_citations from read passages.')
        elif result.get('status')=='answered':
            errors.append('Cannot return answered while a conflict is unresolved.')
    return errors
