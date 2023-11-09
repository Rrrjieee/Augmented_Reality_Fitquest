import json
import admin.app_config as app_config

from exercise_details import ExerciseDetails
from routine_details import RoutineDetails
from user_details import UserDetails

class JSONExercise:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance    = super(JSONExercise, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.json_name_path     = app_config.json['name']
        self.json_path          = app_config.json['content']
        self.json_file          = open(self.json_path, 'r')
        if self.json_file is None:
            self.json_list      = []
            return
        self.json_file.close()
        
        with open(self.json_path, "r") as json_file:
            self.json_list      = json.load(json_file)

        for i in range(len(self.json_list)):
            exer_dict           = self.json_list[i]
            self.json_list[i]   = ExerciseDetails.convert(exer_dict)

        self.update()

    def extract_list(self) -> list[ExerciseDetails]:
        ret_list    = []
        for exercise in self.json_list:
            ret_list.append(exercise)
        return ret_list
    
    def extract_names(self) -> list[str]:
        ret_list    = []
        for names in self.json_list:
            ret_list.append(names.name)
        return ret_list
    
    def update(self):
        # Perform a write operation on exercises.json
        content_list        = []
        content_dict        = {
            'exercise'      : [],
        }
        for exer_dict in self.json_list:
            exer_dict: ExerciseDetails
            exer_copy       = {
                'name'          : exer_dict.name,
                'reps'          : exer_dict.reps,
                'sets'          : exer_dict.sets,
                'duration'      : exer_dict.duration,
                'description'   : exer_dict.description,
                'image_path'    : exer_dict.img_path,
            }
            content_dict['exercise'].append(exer_dict.name)

            if exer_dict.body is not None:
                for i in range(len(exer_dict.body)):
                    exer_copy[f'bodypart{i + 1}']   = exer_dict.body[i]

            if exer_dict.angle is not None:
                for i in range(len(exer_dict.angle)):
                    exer_copy[f'angle{i + 1}']   = exer_dict.angle[i]

            content_list.append(exer_copy)

        content             = json.dumps(content_list, indent = 4)
        names               = json.dumps(content_dict, indent = 4)

        with open(self.json_path, 'w') as json_file:
            json_file.write(content)
        with open(self.json_name_path, 'w') as json_file:
            json_file.write(names)

    def get_exercise(self, exer_name: str) -> ExerciseDetails:
        for exercise_dict in self.json_list:
            if exercise_dict.name == exer_name:
                return exercise_dict
            
        return None

    def remove_exercise(self, exer_name: str):
        exer_dict   = self.get_exercise(exer_name)
        if exer_dict is None:
            return
            
        self.json_list.remove(exer_dict)
        del exer_dict
        self.update()
    
    def add_exercise(self,
                     exer_name: str,
                     exer_reps: int,
                     exer_sets: int,
                     exer_dur : int,
                     exer_desc: str,
                     body_arr : list[str] = None,
                     angle_arr: list[float] = None):
        # Check if the exercise already exists in json_list.
        new_exer_dict   = None
        for exercise_dict in self.json_list:
            if exercise_dict.name == exer_name:
                new_exer_dict   = exercise_dict
                break

        if (new_exer_dict is not None):
            new_exer_dict.reps          = exer_reps
            new_exer_dict.sets          = exer_sets
            new_exer_dict.duration      = exer_dur
            new_exer_dict.description   = exer_desc
            new_exer_dict.set_exercise_dict_params(
                                          body_arr,
                                          angle_arr)
            return new_exer_dict
        
        new_exer_dict   = ExerciseDetails(
            exer_name   = exer_name,
            exer_reps   = exer_reps,
            exer_sets   = exer_sets,
            exer_dur    = exer_dur,
            exer_desc   = exer_desc,
        )
        new_exer_dict.set_exercise_dict_params(body_arr,
                                      angle_arr)
        
        self.json_list.append(new_exer_dict)
        self.update()
        return new_exer_dict

# This class must operate after JSONExercise
class JSONRoutine:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance    = super(JSONRoutine, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.json_path  = app_config.json['routines']
        self.json_file  = open(self.json_path, 'r')
        if self.json_file is None:
            self.json_list  = []
        else:
            self.json_list  = json.load(self.json_file)
        self.json_file.close()

        # Parse routine objects.
        self.rout_list  = []
        for routine_dict in self.json_list:
            # Convert entries in routine_dict['exercises'] into valid
            # ExerciseDetails objects.
            exer_list   = routine_dict['exercises']
            
            if exer_list is None:
                rout_object = RoutineDetails(
                    routine_dict['routine_name'],
                    routine_dict['routine_description'],
                    []
                )
                self.rout_list.append(rout_object)
                continue
            
            for i in range(len(exer_list)):
                exercise            = exer_list[i]
                base_obj            = JSONExercise().get_exercise(exercise['name'])
                if base_obj is None:
                    raise ValueError(f"The exercise ({exercise['name']}) has not been registered to the system yet.")
                
                exer_obj            = base_obj.copy()
                exer_obj.sets       = int(exercise['sets'])
                exer_obj.reps       = int(exercise['reps'])
                # Calculate the duration based on the baseline exercise duration.
                exer_obj.duration   = int(base_obj.duration)

                exer_list[i]        = exer_obj

            rout_object     = RoutineDetails(
                routine_dict['routine_name'],
                routine_dict['routine_description'],
                exer_list
            )
            self.rout_list.append(rout_object)

    def extract_list(self) -> list[RoutineDetails]:
        ret_list    = []
        for routine in self.rout_list:
            ret_list.append(routine)
        return ret_list
    
class JSONUser:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance    = super(JSONUser, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized   = True
        self.json_path      = app_config.json['user']
        self.json_file      = open(self.json_path, 'r')
        if self.json_file is None:
            self.json_list  = []
        else:
            self.json_list  = json.load(self.json_file)
        self.json_file.close()

        # Parse User objects.
        self.user_list      = []
        # Returns a singleton object, not to worry!
        json_exer           = JSONExercise()
        for user_dict in self.json_list:
            user            = UserDetails(user_dict['username'])
            user_exer_list  = user_dict['exercises']
            self.user_list.append(user)

            exercise        = None
            for user_dict in user_exer_list:
                # Search for exercise object in user_exer_list
                exercise    = json_exer.get_exercise(user_dict['name'])
                if exercise is None:
                    raise ValueError(f"\nCould not find the given exercise {user_dict['name']} in {app_config.json['content']}. Please add them directly or through the app.")

                user.add_exercise(exercise, user_dict['score'])
        
    def extract_list(self) -> list[UserDetails]:
        ret_list    = []
        for user in self.user_list:
            ret_list.append(user)
        return ret_list
    
    def get_user(self, query_username: str) -> UserDetails|None:
        for user in self.user_list:
            if user.username    == query_username:
                return user
        return None
    
    def get_user_count(self) -> int:
        return len(self.user_list)
    
    def update(self):
        content = []
        for user in self.user_list:
            user_dict   = {
                'username'  : user.username,
                'exercises' : [],
            }
            user_dict_exer  = user_dict['exercises']
            for exercise in user.exercises:
                user_dict_exer.append(exercise)

            content.append(user_dict)

        # Perform a write operation on users.json
        users   = json.dumps(content, indent = 4)
        with open(self.json_path, 'w') as json_file:
            json_file.write(users)