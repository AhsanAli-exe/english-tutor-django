import json


MAX_HISTORY = 20


class Conversation:
    def __init__(self,system_prompt=None):
        self.history = []
        if system_prompt:
            self.history.append({"role":"system","content":system_prompt})
            
    def add_user(self,text):
        self.history.append({"role":"user","content":text})
        self._trim()
        
    def add_assistant(self,text):
        self.history.append({"role":"assistant","content":text})
        self._trim()
        
    def _trim(self,max_history=MAX_HISTORY):
        if len(self.history) > max_history:
            start = 1 if self.history[0]["role"] == "system" else 0
            keep_system = self.history[:start]
            keep_recent = self.history[-(max_history - start):]
            self.history = keep_system + keep_recent
    
    def to_payload(self):
        return self.history.copy()
    
    def save(self,path):
        try:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(self.history,f,ensure_ascii=False,indent=2)
        except Exception as e:
            print(f"Failed to save history {e}")
    
    def load(self,path):
        if path.exists():
            try:
                with open(path,"r",encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Failed to load history {e}")
