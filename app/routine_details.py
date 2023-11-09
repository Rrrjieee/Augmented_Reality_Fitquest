from exercise_details import ExerciseDetails
class RoutineDetails:
    def __init__(self,
                 name: str,
                 desc: str,
                 exercises: list[ExerciseDetails] = None):
        self.routine_name           = name
        self.routine_description    = desc
        self.exercises              = exercises

    def add_exercise(self, exercise: ExerciseDetails):
        if self.exercises is None:
            self.exercises          = []
        self.exercises.append(exercise)

    def __iter__(self):
        self._index     = 0
        return self
    
    def __next__(self):
        if ((self.exercises is None) or
            (self._index >= len(self.exercises))):
            del self._index
            raise StopIteration

        result          = self.exercises[self._index]
        self._index    += 1
        return result
    
    def iterator(self):
        if self.exercises is None:
            return None
        
        i   = 0
        while i < len(self.exercises):
            yield self.exercises[i]
            i += 1

    def copy(self):
        obj = RoutineDetails(
            name        = self.routine_name,
            desc        = self.routine_description,
            exercises   = []
        )
        for exercise in iter(self):
            obj.add_exercise(exercise)
        return obj