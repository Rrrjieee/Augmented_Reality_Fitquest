from exercise_details import ExerciseDetails

class UserDetails:
    def __init__(self,
                 name: str):
        self.username   = name
        self.exercises  = []

    def add_exercise(self,
                     exercise: ExerciseDetails,
                     avg_list: list[float] | float):
        '''
        Adds an exercise to the user's list of performed
        exercises, and updates the score history of the
        specified exercise.
        '''
        _index  = -1
        # Due to recursive imports, we can't use
        # JSONExercise().get_exercise(exercise.name)
        for i in range(len(self.exercises)):
            iter_exercise   = self.exercises[i]
            if iter_exercise['name'] == exercise.name:
                _index      = i
                break

        if _index > -1:
            # Found a result.
            iter_dict       = self.exercises[_index]
            iter_list       = iter_dict['score']
            if isinstance(avg_list, float):
                iter_list.append(avg_list)
            else:
                for score in avg_list:
                    iter_list.append(score)
            return

        iter_dict           = {
            'name'          : exercise.name,
        }
        if isinstance(avg_list, float):
            iter_dict['score']  = [avg_list]
        else:
            iter_dict['score']  = avg_list[:]
        self.exercises.append(iter_dict)

    def get_exercise_list(self) -> list[dict[str, str]]:
        '''
        Creates a new list that contains all registered
        exercises. Cleaning up the list object is up to
        the user.

        Dictionary object fields:
            'name'  : str   - used to point towards the relevant ExerciseDetails

            'score' : []    - stores all previously registered average scores.
        '''
        ret_list    = []
        for exer_dict in self.exercises:
            ret_list.append(exer_dict)
        return ret_list