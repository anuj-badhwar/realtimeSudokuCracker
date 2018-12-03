import cv2
from imageProcess import *
from Classfier import *
from Sudoku import solve
show_solution = True

def video_test():
    mapped_size = (252, 252)
    global_step = 20000
    predictor = get_trained_model()
    cap = cv2.VideoCapture(0)

    valid_count = 0
    invalid_count = 0
    digits_history_flag = []
    block_center = {}
    cache_digits_flag = None
    cache_solution = None
    reset = True
    while (cap.isOpened()):
        ret, frame = cap.read()
        recs = get_rectangles(frame)

        if len(recs)>0:
            isValid=False
            valid_rectangle = None
            for rec in recs:
                digits_flag = []
                rotational_matrix = get_rotational_matrix(rec[0], mapped_size, reverse=False)
                mapped = cv2.warpPerspective(frame, rotational_matrix, mapped_size)
                binary_mapped = preprocess_sudoku_grid(mapped)
                binary_blocks = split_2_blocks(binary_mapped,9,9)
                for i, b in enumerate(binary_blocks):
                    cur_block = b.reshape(28,28)
                    flag,centre = catch_digit_center(cur_block,(16,20))
                    digits_flag.append(flag)
                    if  flag:
                        block_center.setdefault(i,[]).append(centre.flatten())
                if sum(digits_flag) >= 17:
                    isValid = True
                    invalid_count = 0

                    valid_rectangle = rec
                    if not reset and np.sum(digits_flag^cache_digits_flag)<5 and cache_solution is not None:
                        block_center.clear()
                        if show_solution:
                            mapped = write_solution(mapped, merged_digits_flag, cache_solution)

                        frame = reflect_to_orig(frame, rotational_matrix, mapped)

                        cv2.imshow('frame',frame)
                    elif not reset:
                        reset = True
                        valid_count = 0
                        digits_history_flag = []
                        cache_solution = None
                        cache_digits_flag = None
                    break #Dont process further rectangles
            if not isValid:
                invalid_count += 1
                if invalid_count >=3:
                    invalid_count = 3
                    reset = True
                    valid_count = 0
                    digits_history_flag = []
                    block_center.clear()
                    cache_solution = None
                    cache_digits_flag = None
                cv2.imshow('frame', frame)
            elif reset:
                valid_count+=1
                digits_history_flag.append(digits_flag)
                if valid_count > 10:

                    merged_digits_flag = np.sum(np.array(digits_history_flag),axis=0).astype(np.bool)
                    cache_digits_flag = merged_digits_flag
                    reset = False
                    pre_centre_blocks = []
                    for i in xrange(9*9):
                        if merged_digits_flag[i]:
                            pre_centre_blocks.append(np.mean(block_center[i],axis=0))
                    pred_labels = predictor(pre_centre_blocks)+1
                    sudoku = np.zeros(81)
                    sudoku[merged_digits_flag] = pred_labels
                    sudoku = sudoku.astype(np.int)
                    answer = solve(''.join(map(str,sudoku)))
                    if answer is not False and show_solution:
                        cache_solution = answer
                        mapped = write_solution(mapped, merged_digits_flag, answer)
                        cv2.imshow("Write",mapped)

                    frame = reflect_to_orig(frame, rotational_matrix, mapped)
                cv2.imshow('frame', frame)
        else:
            invalid_count += 1
            if invalid_count >= 3:
                invalid_count = 3
                reset = True

                valid_count = 0
                digits_history_flag = []
                block_center.clear()
                cache_solution = None
                cache_digits_flag = None
            cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_test()
