import gym
import requests
from tactics import Tactics

class RafRpg(gym.Env):
  def __init__(self, input_size, number=-1) -> None:
    super().__init__()
    self.input_size = input_size
    self.url_root = "http://localhost:8082"
    self.prev_value = 0
    if number == -1:
        url = self.url_root+"/map/restart"
    else:
      url = self.url_root+f"/map/restart?map_number={number}"
    payload={}
    headers = {}
    response = requests.request("PUT", url, headers=headers, data=payload)
    tt = response.json()
    # print(tt,type(tt))
    self.tactics = Tactics(self.url_root, input_size=self.input_size)

    
  def reset(self,number = -1):
    if number == -1:
      url = self.url_root+"/map/restart"
    else:
      url = self.url_root+f"/map/restart?map_number={number}"
    payload={}
    headers = {}
    response = requests.request("PUT", url, headers=headers, data=payload)
    output = response.json()
    # print(output)
    self.tactics = Tactics(self.url_root, input_size=self.input_size)
    return output

  def step(self,action):

    prev, curr, new_field = self.tactics.step(action)
    reward = self.tactics.get_reward(prev, curr, has_moved=self.tactics.has_moved(action), new_field=new_field)

    is_over = self.tactics.is_over()

    return self.tactics.current_map, reward, is_over, {}

  def render(self):
    payload={}
    headers = {}

    url = self.url_root + "/map/full/matrix"
    response = requests.request("GET", url, headers=headers, data=payload)
    next_observation = response.json()

    return next_observation